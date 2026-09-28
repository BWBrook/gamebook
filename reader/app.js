'use strict';

const $ = (id) => document.getElementById(id);
let bootstrap;
let view = null;
let busy = false;
let quote = '';
let selectedQuote = '';
let draftKey = '';
const drafts = new Map();
const initialSheet = {fortune: 10, stamina: 6, exposure: 0, possessions: ['Sword'], marks: []};

function node(tag, text, className) {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = text;
  if (className) element.className = className;
  return element;
}

function button(text, handler, className) {
  const element = node('button', text, className);
  element.type = 'button';
  element.addEventListener('click', handler);
  return element;
}

const capitalise = (text) => text.charAt(0).toUpperCase() + text.slice(1);

function localRead(key, fallback = '') {
  try { return localStorage.getItem(key) ?? fallback; } catch { return fallback; }
}

function localWrite(key, value) {
  try { localStorage.setItem(key, value); } catch { /* Local files remain the durable record. */ }
}

async function request(path, body) {
  const response = await fetch(path, body === undefined ? {} : {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) {
    const error = new Error(data.error || `The reader returned ${response.status}.`);
    error.status = response.status;
    throw error;
  }
  return data;
}

function setBusy(value) {
  busy = value;
  document.querySelectorAll('button, input, textarea').forEach((element) => {
    if (value) {
      element.dataset.wasDisabled = element.disabled ? '1' : '0';
      element.disabled = true;
    } else if (element.dataset.wasDisabled !== undefined) {
      element.disabled = element.dataset.wasDisabled === '1';
      delete element.dataset.wasDisabled;
    }
  });
  if (value) $('save-status').textContent = 'Saving locally…';
}

async function operate(operation, {focus = true, action = null} = {}) {
  if (busy) return;
  const previousPassage = view?.viewing;
  rememberDraft();
  $('error').hidden = true;
  setBusy(true);
  try {
    const next = await operation();
    if (next) {
      view = next;
      const url = new URL(location.href);
      url.searchParams.set('session', view.id);
      history.replaceState(null, '', url);
    }
    setBusy(false);
    render();
    if (focus) {
      const target = action && previousPassage === view?.viewing ? $('actions') : $('reading');
      // Put the cursor in the die field so a physical roll can be typed and entered at once.
      const field = target === $('actions')
        ? $('actions').querySelector('input[name^="die-"]') || $('actions').querySelector('.fortune-choices button')
        : null;
      (field || target).focus({preventScroll: true});
      if (field?.select) field.select();
      target.scrollIntoView({behavior: 'instant', block: 'start'});
    }
    return true;
  } catch (error) {
    setBusy(false);
    if (error.status === 409 && view) {
      try { view = await request(`/api/sessions/${view.id}`); render(); } catch { /* Retain the original conflict. */ }
    }
    $('error').textContent = error.message || 'Could not reach the local reader. Check that its server is running.';
    $('error').hidden = false;
    $('save-status').textContent = 'Not saved — see message above.';
    return false;
  }
}

function perform(action, payload = {}) {
  return operate(() => request(`/api/sessions/${view.id}/action`, {action, payload, version: view.version}), {action});
}

function review(passage) {
  $('journey-dialog').close();
  return operate(() => request(`/api/sessions/${view.id}?passage=${encodeURIComponent(passage)}`));
}

function currentContext() { return view ? view.viewing : 'rules'; }

function rememberDraft() {
  if (!draftKey) return;
  const draft = {text: $('note-text').value, quote};
  drafts.set(draftKey, draft);
  localWrite(draftKey, JSON.stringify(draft));
}

function restoreDraft() {
  draftKey = view ? `tower-note:${view.id}:${currentContext()}` : '';
  let draft = drafts.get(draftKey);
  if (!draft && draftKey) {
    try { draft = JSON.parse(localRead(draftKey, '{}')); } catch { draft = {}; }
  }
  $('note-text').value = draft?.text || '';
  quote = draft?.quote || '';
  renderQuote();
}

function renderQuote() {
  $('note-quote').textContent = quote;
  $('note-quote').hidden = !quote;
  $('clear-quote').hidden = !quote;
}

function renderSheet() {
  const state = view?.state || initialSheet;
  $('resources').replaceChildren();
  for (const [key, label, maximum] of [['fortune', 'Fortune', 10], ['stamina', 'Stamina', 6], ['exposure', 'Exposure', 5]]) {
    const value = state[key];
    const group = node('div', undefined, `resource ${key}`);
    const row = node('div', undefined, 'resource-label');
    row.append(node('span', label), node('span', `${value} / ${maximum}`));
    const pips = node('div', undefined, 'pips');
    pips.setAttribute('aria-hidden', 'true');
    for (let i = 0; i < maximum; i++) pips.append(node('span', undefined, `pip${i < value ? ' filled' : ''}`));
    group.append(row, pips);
    if (key === 'exposure') group.append(node('p', value < 3 ? 'Hidden in the night' : value < 5 ? 'The watch is looking' : 'Discovered', 'exposure-caption'));
    $('resources').append(group);
  }
  $('inventory').replaceChildren();
  for (const [title, entries] of [['Possessions', state.possessions], ['Story marks', state.marks]]) {
    const group = node('section');
    group.append(node('h3', title));
    if (entries?.length) {
      const list = node('ul');
      for (const entry of entries) list.append(node('li', entry));
      group.append(list);
    } else group.append(node('p', 'None yet', 'empty'));
    $('inventory').append(group);
  }
  $('report-link').hidden = !view;
  $('new-button').hidden = !view;
  if (view) {
    $('report-link').href = `/api/sessions/${view.id}/report`;
    $('save-status').textContent = `Saved on this Mac · ${new Date(view.updated_at).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}`;
  } else $('save-status').textContent = 'Ready when you are. No reading started.';
}

function renderSessions(container, sessions) {
  container.replaceChildren();
  for (const session of sessions) {
    if (session.error) {
      const damaged = button(session.label, () => {}, 'resume-button');
      damaged.disabled = true;
      damaged.append(node('small', session.error));
      container.append(damaged);
      continue;
    }
    const item = button(session.label, () => {
      $('journey-dialog').close();
      operate(() => request(`/api/sessions/${session.id}`));
    }, 'resume-button');
    item.append(node('small', `${session.passage} · ${session.phase === 'ended' ? 'Ended' : 'In progress'} · ${session.note_count} note${session.note_count === 1 ? '' : 's'} · ${new Date(session.updated_at).toLocaleDateString()}`));
    container.append(item);
  }
}

function render() {
  renderSheet();
  $('welcome').hidden = !!view;
  $('passage-heading').replaceChildren();
  $('reading-banner').replaceChildren();
  $('reading-banner').hidden = true;
  $('revision').textContent = view ? `Text revision ${view.source_revision.slice(0, 10)}` : 'Robert E. Howard · Adapted by Barry W. Brook';
  $('rules-button').textContent = view?.viewing === 'rules' ? (view.last_event ? 'Back to story' : 'Begin at S01') : 'Rules';
  $('rules-button').hidden = !view;
  if (!view) {
    $('passage').replaceChildren();
    renderSessions($('resume-list'), bootstrap.sessions);
    if (bootstrap.sessions.length) $('resume-list').prepend(node('h3', 'Continue an earlier reading'));
  } else {
    if (view.viewing !== 'rules') {
      $('passage-heading').append(node('p', view.passage.id, 'eyebrow'), node('h1', view.passage.title));
    }
    $('passage').innerHTML = view.passage.html;
    if (view.read_only || view.viewing === 'rules') {
      const fresh = !view.last_event;
      $('reading-banner').hidden = false;
      const description = view.read_only_reason || (view.viewing === 'rules'
        ? (fresh ? 'Read the rules before you begin. Highlight anything unclear to leave a note.' : 'The rules for this reading. Your place in the adventure is saved.')
        : `Reviewing ${view.viewing}. Your current passage is ${view.state.passage}; the sheet shows your current state.`);
      $('reading-banner').append(node('span', description));
      if (view.viewing !== view.state.passage) {
        $('reading-banner').append(button(fresh && !view.read_only_reason ? 'Begin at S01' : `Return to ${view.state.passage}`, () => review(view.state.passage)));
      }
    }
  }
  // Printed passage references are reading material; only authored action controls advance play.
  $('passage').querySelectorAll('a').forEach((link) => {
    if (/^(#|S\d)/.test(link.getAttribute('href') || '')) link.replaceWith(node('span', link.textContent));
  });
  selectedQuote = '';
  $('selection-note').hidden = true;
  restoreDraft();
  renderActions();
  renderNotes();
  if (busy) setBusy(true);
}

function renderActions() {
  const actions = $('actions');
  actions.replaceChildren();
  if (!view) return;
  if (view.viewing === 'rules' && !view.read_only_reason) {
    const fresh = !view.last_event;
    actions.append(node('h2', fresh ? 'Ready to enter the garden?' : 'Back to the adventure'),
      button(fresh ? 'Begin at S01' : `Return to ${view.state.passage}`, () => review(view.state.passage), 'primary'));
    return;
  }
  if (view.read_only) return;
  const {state} = view;
  const changes = view.last_event?.detail?.changes || [];
  if (changes.length && state.phase !== 'result') {
    const update = node('div', undefined, 'sheet-update');
    update.append(node('h3', 'Adventure Sheet updated'));
    const list = node('ul', undefined, 'change-list');
    changes.forEach((change) => list.append(node('li', change)));
    update.append(list);
    actions.append(update);
  }
  if (state.phase === 'choice') {
    actions.append(node('h2', 'Choose your action'));
    for (const choice of view.choices) {
      const control = button(choice.label, () => perform('choose', {choice_id: choice.id}), 'choice');
      control.disabled = !choice.enabled;
      if (!choice.enabled && choice.reason) control.append(node('small', choice.reason));
      else if (choice.roll) control.append(node('small', `Test ${choice.roll.attribute} ${choice.roll.target}${choice.roll.mode !== 'standard' ? ` with ${capitalise(choice.roll.mode)}` : ''}`));
      else if (choice.hint) control.append(node('small', choice.hint));
      actions.append(control);
    }
    return;
  }
  const panel = node('div', undefined, 'mechanic-panel');
  actions.append(panel);
  if (state.phase === 'dice') {
    const roll = state.pending.roll;
    const count = roll.mode === 'standard' ? 1 : 2;
    panel.append(node('h2', 'Make a physical roll'), node('p', `${state.pending.label}. Roll ${count === 1 ? 'one d20' : 'two d20s'} against ${roll.attribute} ${roll.target}.${count === 2 ? ` With ${roll.mode}, keep the ${roll.mode === 'advantage' ? 'lower' : 'higher'} die.` : ''} Enter the faces exactly as rolled.`));
    const form = node('form');
    const fields = node('div', undefined, 'dice-fields');
    for (let i = 0; i < count; i++) {
      const label = node('label', count === 1 ? 'Your d20' : `Die ${i + 1}`);
      const input = node('input');
      Object.assign(input, {type: 'number', min: '1', max: '20', step: '1', required: true, name: `die-${i}`, inputMode: 'numeric'});
      label.append(input); fields.append(label);
    }
    const submit = node('button', 'Record roll', 'primary'); submit.type = 'submit';
    form.append(fields, submit);
    form.addEventListener('submit', (event) => { event.preventDefault(); perform('roll', {dice: [...fields.querySelectorAll('input')].map((input) => Number(input.value))}); });
    panel.append(form);
  } else if (state.phase === 'fortune') {
    const pending = state.pending;
    const roll = pending.roll;
    const kept = pending.resolved.selected_die;
    const needed = Math.max(0, kept - roll.target);
    const standing = needed ? `a failure by ${needed}` : 'a success';
    const advice = !needed ? '' : needed <= state.fortune
      ? ` Spending ${needed} Fortune turns it into a success.`
      : ` You have ${state.fortune} Fortune, not enough to change it.`;
    panel.append(node('h2', 'Spend Fortune?'), node('p', `You kept ${kept} against ${roll.attribute} ${roll.target}: ${standing}.${advice}`));
    const quick = node('div', undefined, 'fortune-choices');
    if (needed && needed <= state.fortune) quick.append(button(`Spend ${needed} Fortune and succeed`, () => perform('fortune', {spend: needed}), 'primary'));
    quick.append(button(needed ? 'Keep the failure' : 'Keep the success', () => perform('fortune', {spend: 0}), needed && needed <= state.fortune ? '' : 'primary'));
    panel.append(quick);
    const form = node('form', undefined, 'fortune-custom');
    const fields = node('div', undefined, 'dice-fields');
    const label = node('label', 'Or spend another amount');
    const input = node('input');
    Object.assign(input, {type: 'number', min: '0', max: String(state.fortune), step: '1', required: true, value: '0', inputMode: 'numeric'});
    label.append(input); fields.append(label);
    const preview = node('p', undefined, 'fortune-preview');
    const update = () => { const final = kept - Number(input.value); preview.textContent = `Final die ${final} · Margin ${roll.target - final} · ${final <= roll.target ? 'Success' : 'Failure'}`; };
    input.addEventListener('input', update); update();
    const submit = node('button', 'Spend this amount'); submit.type = 'submit';
    form.append(fields, preview, submit);
    form.addEventListener('submit', (event) => { event.preventDefault(); perform('fortune', {spend: Number(input.value)}); });
    panel.append(form);
  } else if (state.phase === 'result') {
    const result = state.result;
    const resolved = state.pending?.resolved;
    panel.append(node('h2', result.outcome ? capitalise(result.outcome) : 'Result'));
    if (resolved) {
      const spent = resolved.fortune_spent ? `, lowered to ${resolved.final_die} with ${resolved.fortune_spent} Fortune` : '';
      const locked = resolved.natural ? ' Fortune cannot change a natural result.' : '';
      panel.append(node('p', `You kept ${resolved.selected_die}${spent}, against ${resolved.attribute} ${resolved.target}.${locked}`, 'muted'));
    }
    if (view.result_html) {
      const printed = node('div', undefined, 'printed-result');
      printed.innerHTML = view.result_html;
      panel.append(printed);
    }
    if (result.changes?.length) { const list = node('ul', undefined, 'change-list'); result.changes.forEach((change) => list.append(node('li', change))); panel.append(list); }
    panel.append(button(`Continue to ${result.destination}`, () => perform('continue'), 'primary'));
  } else if (state.phase === 'ended') {
    panel.append(node('h2', 'This reading has ended'), node('p', 'Your route, rolls and notes are saved. Leave any final thoughts here, or download the reading report from the Adventure Sheet.'), button('Begin another reading', newReading));
  }
}

function renderNotes() {
  const notes = view?.notes || [];
  const shown = $('all-notes').checked ? notes : notes.filter((note) => note.passage === currentContext());
  $('note-count').textContent = String(notes.length);
  $('note-context').textContent = view ? `Note on ${currentContext() === 'rules' ? 'the rules' : currentContext()}` : 'Notes become available when you begin';
  $('note-text').disabled = !view;
  $('save-note').disabled = !view;
  $('note-status').textContent = view ? 'Saved notes go into your local reading report.' : 'Begin an adventure to keep notes with its reading.';
  $('notes-list').replaceChildren();
  if (!shown.length) $('notes-list').append(node('p', view ? 'No notes here yet.' : 'Your feedback will appear here.', 'muted'));
  for (const note of shown) {
    const card = node('section', undefined, 'saved-note'); card.id = `note-${note.id}`;
    card.append(node('div', `${note.passage === 'rules' ? 'Rules' : note.passage} · ${new Date(note.created_at).toLocaleString([], {dateStyle: 'medium', timeStyle: 'short'})}`, 'note-meta'));
    if (note.quote) card.append(node('blockquote', note.quote));
    card.append(node('p', note.text)); $('notes-list').append(card);
  }
  $('passage').querySelectorAll('.note-marker').forEach((marker) => marker.remove());
  for (const note of notes.filter((item) => item.passage === currentContext() && item.quote)) {
    const paragraph = [...$('passage').querySelectorAll('p, li')].find((element) => element.textContent.replace(/\s+/g, ' ').includes(note.quote));
    if (!paragraph) continue;
    const marker = button('✎', () => {
      showNotes(true); $('all-notes').checked = false; renderNotes();
      const card = $(`note-${note.id}`); card?.classList.add('focused'); card?.scrollIntoView({block: 'nearest'});
    }, 'note-marker');
    marker.setAttribute('aria-label', `Read note: ${note.text.slice(0, 80)}`);
    paragraph.append(marker);
  }
}

function showNotes(open) {
  document.body.classList.toggle('notes-closed', !open);
  $('notes-button').setAttribute('aria-expanded', String(open));
}

async function newReading() {
  rememberDraft();
  await operate(async () => {
    bootstrap = await request('/api/bootstrap'); view = null;
    const url = new URL(location.href); url.searchParams.delete('session'); history.replaceState(null, '', url);
  });
}

$('begin-form').addEventListener('submit', (event) => {
  event.preventDefault();
  // Open on the rules so the primer can be annotated before play begins.
  operate(async () => {
    const created = await request('/api/sessions', {label: $('reading-label').value});
    return request(`/api/sessions/${created.id}?passage=rules`);
  });
});
$('new-button').addEventListener('click', newReading);
$('rules-button').addEventListener('click', () => {
  if (view) review(view.viewing === 'rules' ? view.state.passage : 'rules');
  else $('passage').scrollIntoView({block: 'start'});
});
$('notes-button').addEventListener('click', () => {
  const open = document.body.classList.contains('notes-closed'); showNotes(open);
  if (open && innerWidth < 950) $('notes-panel').scrollIntoView({block: 'start'});
});
$('close-journey').addEventListener('click', () => $('journey-dialog').close());
$('journey-button').addEventListener('click', async () => {
  $('journey-list').replaceChildren();
  if (view) {
    for (const passage of view.history) {
      const entry = button('', () => review(passage.id), 'journey-entry');
      entry.append(node('span', passage.id), document.createTextNode(`${passage.title}${passage.id === view.state.passage ? ' · Current' : ''}`));
      $('journey-list').append(entry);
    }
  } else $('journey-list').append(node('p', 'Your journey begins when you start the adventure.', 'muted'));
  $('other-sessions').replaceChildren(node('p', 'Loading saved readings…', 'muted'));
  $('journey-dialog').showModal();
  try {
    bootstrap = await request('/api/bootstrap');
    renderSessions($('other-sessions'), bootstrap.sessions.filter((session) => session.id !== view?.id));
    if ($('other-sessions').children.length) $('other-sessions').prepend(node('h3', 'Other readings'));
  } catch { $('other-sessions').replaceChildren(node('p', 'Saved readings could not be loaded.', 'muted')); }
});
$('all-notes').addEventListener('change', renderNotes);
$('note-text').addEventListener('input', rememberDraft);
$('note-text').addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) { event.preventDefault(); $('note-form').requestSubmit(); }
});
$('clear-quote').addEventListener('click', () => { quote = ''; renderQuote(); rememberDraft(); });
function passageSelection() {
  const selection = window.getSelection();
  const passage = $('passage');
  if (!view || !selection || selection.isCollapsed || !selection.rangeCount) return '';
  // Triple-click and long drags end outside the passage; keep only the passage's share.
  const range = selection.getRangeAt(0).cloneRange();
  if (!range.intersectsNode(passage)) return '';
  if (!passage.contains(range.startContainer)) range.setStart(passage, 0);
  if (!passage.contains(range.endContainer)) range.setEnd(passage, passage.childNodes.length);
  const selected = range.cloneContents();
  selected.querySelectorAll('.note-marker').forEach((marker) => marker.remove());
  selected.querySelectorAll('p, li, h1, h2, h3, blockquote, br').forEach((element) => {
    element.before(document.createTextNode(' '));
    element.after(document.createTextNode(' '));
  });
  return selected.textContent.replace(/\s+/g, ' ').trim();
}
document.addEventListener('selectionchange', () => {
  selectedQuote = passageSelection();
  $('selection-note').hidden = !selectedQuote;
});
$('selection-note').addEventListener('pointerdown', (event) => event.preventDefault());
$('selection-note').addEventListener('click', () => {
  if (!selectedQuote) return;
  quote = selectedQuote; renderQuote(); rememberDraft(); showNotes(true);
  $('note-text').focus();
});
$('note-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!view || !$('note-text').value.trim()) { $('note-text').focus(); return; }
  const savedKey = draftKey;
  const payload = {text: $('note-text').value, quote, passage: currentContext(), version: view.version};
  const success = await operate(() => request(`/api/sessions/${view.id}/notes`, payload), {focus: false});
  if (success) {
    drafts.delete(savedKey); localWrite(savedKey, '{}');
    if (savedKey === draftKey) { $('note-text').value = ''; quote = ''; renderQuote(); }
    $('note-status').textContent = 'Note saved on this Mac.';
  }
});
window.addEventListener('beforeunload', rememberDraft);
let textSize = Number(localRead('tower-text-size', '21'));
if (!Number.isFinite(textSize)) textSize = 21;
function resizeText(delta = 0) {
  textSize = Math.min(36, Math.max(16, textSize + delta));
  document.documentElement.style.setProperty('--reading-size', `${textSize}px`);
  localWrite('tower-text-size', String(textSize));
}
$('smaller-button').addEventListener('click', () => resizeText(-2));
$('larger-button').addEventListener('click', () => resizeText(2));
resizeText();
new ResizeObserver(([entry]) => {
  document.documentElement.style.setProperty('--header-height', `${entry.target.getBoundingClientRect().height}px`);
}).observe(document.querySelector('.topbar'));
if (innerWidth < 650) $('sheet-details').open = false;
window.matchMedia('(max-width: 650px)').addEventListener('change', (event) => {
  $('sheet-details').open = !event.matches;
});
if (innerWidth < 950) showNotes(false);

(async () => {
  try {
    bootstrap = await request('/api/bootstrap');
    const session = new URLSearchParams(location.search).get('session');
    if (session) view = await request(`/api/sessions/${encodeURIComponent(session)}`);
    render();
  } catch (error) {
    $('error').textContent = error.message || 'The local reader could not be loaded.';
    $('error').hidden = false;
    $('save-status').textContent = 'Reader unavailable. Check the local server.';
  }
})();
