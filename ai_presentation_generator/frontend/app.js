/**
 * PresentAI - Neural Presentation Engine Frontend Controller
 * Connects modern UI to Python/FastAPI backend & Deep Learning models.
 */

// Application State
let currentPresentation = null;
let currentSlideIndex = 0;
let currentFilter = 'All';

// Initialize on DOM Load
document.addEventListener('DOMContentLoaded', () => {
  updateLivePreview();
  seedInitialHistory();
  renderHistoryCards();
  checkBackendHealth();
});

// Check API Health & Hardware Device
async function checkBackendHealth() {
  try {
    const res = await fetch('/health');
    if (res.ok) {
      const data = await res.json();
      const dev = data.system?.execution_device || 'MPS';
      const devEl = document.getElementById('device-indicator');
      const platformDevEl = document.getElementById('platform-device-text');
      if (devEl) devEl.innerText = `${dev} Accelerated`;
      if (platformDevEl) platformDevEl.innerText = `${dev} Accelerated (Deep Learning)`;
    }
  } catch (err) {
    console.warn('Backend running in local/standalone mode.');
  }
}

// ==========================================================================
// Navigation Controller
// ==========================================================================
function navigateTo(screenName) {
  const screens = document.querySelectorAll('.screen-view');
  screens.forEach(s => s.classList.remove('active'));

  const target = document.getElementById(`screen-${screenName}`);
  if (target) {
    target.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // Update navbar buttons
  document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
  const activeNavBtn = document.getElementById(`nav-btn-${screenName}`);
  if (activeNavBtn) activeNavBtn.classList.add('active');
}

// ==========================================================================
// Presets Toolbar Controller
// ==========================================================================
function applyPreset(presetType) {
  const topicInput = document.getElementById('input-topic');
  const objectiveInput = document.getElementById('input-objective');
  const audienceSelect = document.getElementById('select-audience');
  const typeSelect = document.getElementById('select-type');
  const slidesSlider = document.getElementById('range-slides');
  const durationSlider = document.getElementById('range-duration');

  document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));

  if (presetType === 'healthcare') {
    document.getElementById('preset-btn-healthcare')?.classList.add('active');
    topicInput.value = 'Artificial Intelligence in Healthcare';
    objectiveInput.value = 'Explain how AI is transforming healthcare diagnosis, clinical decisions, and patient outcomes';
    audienceSelect.value = 'Industry Professionals';
    typeSelect.value = 'Executive Briefing';
    document.getElementById('diff-intermediate').checked = true;
    slidesSlider.value = 8;
    durationSlider.value = 12;
  } else if (presetType === 'autonomous_driving') {
    document.getElementById('preset-btn-autodrive')?.classList.add('active');
    topicInput.value = 'Autonomous Vehicles & Smart Mobility';
    objectiveInput.value = 'Analyze perception systems, sensor fusion, safety validation, and commercial deployment of self-driving fleets';
    audienceSelect.value = 'Corporate Executives';
    typeSelect.value = 'Executive Briefing';
    document.getElementById('diff-advanced').checked = true;
    slidesSlider.value = 10;
    durationSlider.value = 15;
  } else if (presetType === 'clean_energy') {
    document.getElementById('preset-btn-energy')?.classList.add('active');
    topicInput.value = 'Clean Energy Transition & Smart Grids';
    objectiveInput.value = 'Examine utility-scale renewables, grid battery storage economics, and decarbonization strategies';
    audienceSelect.value = 'Corporate Executives';
    typeSelect.value = 'Executive Briefing';
    document.getElementById('diff-intermediate').checked = true;
    slidesSlider.value = 6;
    durationSlider.value = 10;
  } else if (presetType === 'enterprise_saas') {
    document.getElementById('preset-btn-cloud')?.classList.add('active');
    topicInput.value = 'Enterprise Cloud Architecture & Strategy';
    objectiveInput.value = 'Review cloud modernization roadmaps, microservice scalability, and enterprise data governance';
    audienceSelect.value = 'Technical Teams';
    typeSelect.value = 'Case Study';
    document.getElementById('diff-advanced').checked = true;
    slidesSlider.value = 8;
    durationSlider.value = 15;
  }

  document.getElementById('val-slides').innerText = `${slidesSlider.value} slides`;
  document.getElementById('val-duration').innerText = `${durationSlider.value} mins`;
  updateLivePreview();
}

// ==========================================================================
// Screen 2: Live Preview Updates
// ==========================================================================
function updateLivePreview() {
  const topic = document.getElementById('input-topic')?.value.trim() || 'Your Presentation Topic';
  const objective = document.getElementById('input-objective')?.value.trim() || 'Describe presentation goals...';
  const slides = document.getElementById('range-slides')?.value || 8;
  const duration = document.getElementById('range-duration')?.value || 12;
  const audience = document.getElementById('select-audience')?.value || 'College Students';

  const topicEl = document.getElementById('preview-topic-title');
  const objEl = document.getElementById('preview-objective-text');
  const slidesEl = document.getElementById('preview-stat-slides');
  const durEl = document.getElementById('preview-stat-duration');
  const paceEl = document.getElementById('preview-stat-pace');
  const audEl = document.getElementById('preview-stat-audience');
  const domainEl = document.getElementById('preview-domain-tag');

  if (topicEl) topicEl.innerText = topic;
  if (objEl) objEl.innerText = objective;
  if (slidesEl) slidesEl.innerText = slides;
  if (durEl) durEl.innerText = `${duration} min`;
  if (paceEl) paceEl.innerText = `${(duration / slides).toFixed(1)} m/slide`;
  if (audEl) audEl.innerText = audience.split(' ')[0];

  // Domain detection heuristic
  if (domainEl) {
    const tLower = topic.toLowerCase();
    if (tLower.includes('health') || tLower.includes('medic') || tLower.includes('doctor')) {
      domainEl.innerText = 'Healthcare';
    } else if (tLower.includes('driv') || tLower.includes('vision') || tLower.includes('vehicle') || tLower.includes('robot')) {
      domainEl.innerText = 'Deep Learning / Robotics';
    } else if (tLower.includes('ai') || tLower.includes('learn') || tLower.includes('neural') || tLower.includes('comput')) {
      domainEl.innerText = 'Deep Learning / Tech';
    } else if (tLower.includes('financ') || tLower.includes('bank') || tLower.includes('crypto')) {
      domainEl.innerText = 'Finance';
    } else if (tLower.includes('climat') || tLower.includes('energy') || tLower.includes('sustain')) {
      domainEl.innerText = 'Environmental Science';
    } else {
      domainEl.innerText = 'Technology / Applied';
    }
  }
}

// ==========================================================================
// Generation Execution
// ==========================================================================
async function handleGenerate(event) {
  if (event) event.preventDefault();

  const errBox = document.getElementById('form-error-banner');
  errBox.style.display = 'none';

  const topic = document.getElementById('input-topic').value.trim();
  const objective = document.getElementById('input-objective').value.trim();
  const audience = document.getElementById('select-audience').value;
  const presentation_type = document.getElementById('select-type').value;
  const difficulty = document.querySelector('input[name="difficulty"]:checked').value;
  const num_slides = parseInt(document.getElementById('range-slides').value, 10);
  const duration = parseInt(document.getElementById('range-duration').value, 10);

  if (!topic || topic.length < 3) {
    errBox.innerText = 'Please enter a valid presentation topic (minimum 3 characters).';
    errBox.style.display = 'block';
    return;
  }
  if (!objective || objective.length < 5) {
    errBox.innerText = 'Please provide an objective describing what the audience will learn.';
    errBox.style.display = 'block';
    return;
  }

  // Switch to Screen 3: Generation State
  navigateTo('generating');
  resetStepper();

  const steps = [
    { id: 'step-1', msg: 'Validating presentation parameters (slide count, pacing, audience)...' },
    { id: 'step-2', msg: 'Structuring narrative outline & logical section progression...' },
    { id: 'step-3', msg: 'Analyzing topic focus & core executive themes...' },
    { id: 'step-4', msg: 'Formulating high-impact arguments & slide headlines...' },
    { id: 'step-5', msg: `Planning exact ${num_slides}-slide sequence (${duration} mins total pacing)...` },
    { id: 'step-6', msg: `Synthesizing slide titles, talking points & applied examples...` },
    { id: 'step-7', msg: 'Polishing content clarity & drafting contextual presenter notes...' },
    { id: 'step-8', msg: 'Finalizing presentation deck & generating export schemas...' },
  ];

  let currentStepIdx = 0;
  const stepInterval = setInterval(() => {
    if (currentStepIdx < steps.length) {
      updateStepperStage(currentStepIdx + 1, steps[currentStepIdx].msg);
      currentStepIdx++;
    }
  }, 900);

  try {
    const payload = {
      topic,
      objective,
      audience,
      difficulty,
      presentation_type,
      num_slides,
      duration,
    };

    const response = await fetch('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    clearInterval(stepInterval);

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: 'Server generation failed' }));
      const msg = typeof errData.detail === 'object' && errData.detail.errors
        ? errData.detail.errors.join(', ')
        : (errData.detail || 'Generation failed');
      throw new Error(msg);
    }

    const data = await response.json();
    currentPresentation = data;

    saveToHistory(data);

    for (let i = 1; i <= 8; i++) {
      const el = document.getElementById(`step-${i}`);
      if (el) {
        el.className = 'step-item completed';
        el.querySelector('.step-icon').innerText = '✓';
      }
    }
    document.getElementById('gen-status-text').innerText = 'Presentation ready!';

    setTimeout(() => {
      renderGeneratedPresentation(data);
      navigateTo('result');
    }, 500);

  } catch (err) {
    clearInterval(stepInterval);
    console.error('Generation Error:', err);
    alert(`Generation Error: ${err.message}. Check backend server status.`);
    navigateTo('create');
    errBox.innerText = `Error: ${err.message}`;
    errBox.style.display = 'block';
  }
}

function resetStepper() {
  for (let i = 1; i <= 8; i++) {
    const el = document.getElementById(`step-${i}`);
    if (el) {
      if (i === 1) {
        el.className = 'step-item active';
        el.querySelector('.step-icon').innerText = '●';
      } else {
        el.className = 'step-item pending';
        el.querySelector('.step-icon').innerText = '○';
      }
    }
  }
  document.getElementById('gen-status-text').innerText = 'Validating presentation configuration...';
}

function updateStepperStage(stepNum, message) {
  document.getElementById('gen-status-text').innerText = message;
  for (let i = 1; i <= 8; i++) {
    const el = document.getElementById(`step-${i}`);
    if (!el) continue;
    if (i < stepNum) {
      el.className = 'step-item completed';
      el.querySelector('.step-icon').innerText = '✓';
    } else if (i === stepNum) {
      el.className = 'step-item active';
      el.querySelector('.step-icon').innerText = '●';
    } else {
      el.className = 'step-item pending';
      el.querySelector('.step-icon').innerText = '○';
    }
  }
}

// ==========================================================================
// Screen 4: Render Generated Presentation
// ==========================================================================
function renderGeneratedPresentation(data) {
  document.getElementById('res-topic-title').innerText = data.topic;
  document.getElementById('res-objective-text').innerText = data.objective || 'Presentation Outline';
  document.getElementById('stat-domain').innerText = data.domain || 'Technology';
  document.getElementById('stat-slides').innerText = data.num_slides || data.slides.length;
  document.getElementById('stat-duration').innerText = `${data.duration} min`;
  document.getElementById('stat-difficulty').innerText = data.difficulty;
  document.getElementById('stat-redundant').innerText = data.points_refined || 0;

  const container = document.getElementById('slides-cards-container');
  container.innerHTML = '';

  data.slides.forEach((slide, idx) => {
    const isExpanded = idx === 0 ? 'expanded' : '';
    const card = document.createElement('div');
    card.className = `slide-card ${isExpanded}`;
    card.id = `slide-card-${idx}`;

    const bulletsHtml = (slide.bullets || [])
      .map(b => `<li>${escapeHtml(b)}</li>`)
      .join('');

    const caseStudyHtml = slide.case_study ? `
      <div class="case-study-box" style="margin-bottom: 16px;">
        <div class="case-tag">Case Study / Real-World Application</div>
        <p>${escapeHtml(slide.case_study)}</p>
      </div>` : '';

    card.innerHTML = `
      <div class="slide-card-header" onclick="toggleSlideCard(${idx})">
        <div class="slide-header-left">
          <span class="slide-number-badge">SLIDE ${String(slide.slide_number).padStart(2, '0')}</span>
          <span class="slide-card-title">${escapeHtml(slide.title)}</span>
        </div>
        <div class="slide-header-right">
          <button class="btn btn-secondary btn-sm card-studio-btn" onclick="event.stopPropagation(); navigateToDetail(${idx})">
            Open in Studio
          </button>
          <span class="slide-time-badge">⏱ ${slide.time_minutes.toFixed(1)} min</span>
          <svg class="chevron-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </div>
      </div>
      <div class="slide-card-body">
        <div class="slide-purpose-box">
          <strong>Purpose:</strong> ${escapeHtml(slide.purpose)}
        </div>
        <div class="slide-content-split">
          <div>
            <div class="section-subhead">Key Discussion Points</div>
            <ul class="key-points-list">
              ${bulletsHtml}
            </ul>
          </div>
        </div>
        ${caseStudyHtml}
        <div class="speaker-notes-box">
          <strong>Speaker Notes:</strong> ${escapeHtml(slide.speaker_notes || '')}
        </div>
      </div>
    `;

    container.appendChild(card);
  });
}

function toggleSlideCard(idx) {
  const card = document.getElementById(`slide-card-${idx}`);
  if (card) {
    card.classList.toggle('expanded');
  }
}

// ==========================================================================
// Screen 5: Slide Detail Presentation View
// ==========================================================================
function navigateToDetail(slideIndex = 0) {
  if (!currentPresentation || !currentPresentation.slides.length) {
    alert('Please select or generate a presentation first.');
    return;
  }

  currentSlideIndex = Math.max(0, Math.min(slideIndex, currentPresentation.slides.length - 1));
  renderDetailNavigation();
  renderCurrentSlideDetail();
  navigateTo('detail');
}

function renderDetailNavigation() {
  const navList = document.getElementById('detail-nav-thumbnails');
  navList.innerHTML = '';

  currentPresentation.slides.forEach((s, idx) => {
    const item = document.createElement('div');
    item.className = `nav-thumbnail ${idx === currentSlideIndex ? 'active' : ''}`;
    item.onclick = () => {
      currentSlideIndex = idx;
      renderDetailNavigation();
      renderCurrentSlideDetail();
    };

    item.innerHTML = `
      <span class="thumb-no">${String(s.slide_number).padStart(2, '0')}</span>
      <span class="thumb-title">${escapeHtml(s.title)}</span>
    `;
    navList.appendChild(item);
  });
}

let isSlideEditing = false;

function resetEditMode() {
  isSlideEditing = false;
  const titleEl = document.getElementById('canvas-title');
  const bullets = document.querySelectorAll('#canvas-bullets li');
  const caseEl = document.getElementById('canvas-case-study');
  const notesEl = document.getElementById('canvas-speaker-notes');
  const btn = document.getElementById('btn-edit-slide');

  if (titleEl) titleEl.contentEditable = "false";
  bullets.forEach(b => b.contentEditable = "false");
  if (caseEl) caseEl.contentEditable = "false";
  if (notesEl) notesEl.contentEditable = "false";

  if (btn) {
    btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg> Edit Content`;
    btn.classList.remove('btn-primary');
  }
}

function renderCurrentSlideDetail() {
  const slide = currentPresentation.slides[currentSlideIndex];
  const total = currentPresentation.slides.length;

  document.getElementById('detail-current-no').innerText = String(slide.slide_number).padStart(2, '0');
  document.getElementById('detail-total-no').innerText = String(total).padStart(2, '0');

  document.getElementById('canvas-badge').innerText = `SLIDE ${String(slide.slide_number).padStart(2, '0')}`;
  document.getElementById('canvas-time').innerText = `⏱ ${slide.time_minutes.toFixed(1)} min`;
  document.getElementById('canvas-title').innerText = slide.title;
  document.getElementById('canvas-purpose').innerText = `Purpose: ${slide.purpose}`;

  const bulletsContainer = document.getElementById('canvas-bullets');
  bulletsContainer.innerHTML = (slide.bullets || []).map(b => `<li>${escapeHtml(b)}</li>`).join('');

  const caseEl = document.getElementById('canvas-case-study');
  const caseContainer = document.getElementById('canvas-case-container');
  if (caseEl) {
    caseEl.innerText = slide.case_study || '';
    if (caseContainer) {
      caseContainer.style.display = slide.case_study ? 'block' : 'none';
    }
  }

  document.getElementById('canvas-speaker-notes').innerText = slide.speaker_notes || '';

  document.getElementById('btn-prev-slide').disabled = currentSlideIndex === 0;
  document.getElementById('btn-next-slide').disabled = currentSlideIndex === total - 1;

  resetEditMode();
}

function navigateSlide(direction) {
  currentSlideIndex += direction;
  renderDetailNavigation();
  renderCurrentSlideDetail();
}

function toggleEditCurrentSlide() {
  const titleEl = document.getElementById('canvas-title');
  const bullets = document.querySelectorAll('#canvas-bullets li');
  const caseEl = document.getElementById('canvas-case-study');
  const notesEl = document.getElementById('canvas-speaker-notes');
  const btn = document.getElementById('btn-edit-slide');

  if (!isSlideEditing) {
    isSlideEditing = true;
    if (titleEl) titleEl.contentEditable = "true";
    bullets.forEach(b => b.contentEditable = "true");
    if (caseEl) caseEl.contentEditable = "true";
    if (notesEl) notesEl.contentEditable = "true";

    titleEl.focus();
    btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg> Save Changes`;
    btn.classList.add('btn-primary');
  } else {
    isSlideEditing = false;
    if (titleEl) titleEl.contentEditable = "false";
    bullets.forEach(b => b.contentEditable = "false");
    if (caseEl) caseEl.contentEditable = "false";
    if (notesEl) notesEl.contentEditable = "false";

    const updatedSlide = currentPresentation.slides[currentSlideIndex];
    if (titleEl && titleEl.innerText.trim()) {
      updatedSlide.title = titleEl.innerText.trim();
    }

    const newBullets = [];
    bullets.forEach(b => {
      const text = b.innerText.trim();
      if (text) newBullets.push(text);
    });
    if (newBullets.length > 0) {
      updatedSlide.bullets = newBullets;
    }

    if (caseEl && caseEl.innerText.trim()) {
      updatedSlide.case_study = caseEl.innerText.trim();
    }
    if (notesEl) {
      updatedSlide.speaker_notes = notesEl.innerText.trim();
    }

    saveToHistory(currentPresentation);
    renderDetailNavigation();
    renderGeneratedPresentation(currentPresentation);

    btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg> Edit Content`;
    btn.classList.remove('btn-primary');
  }
}

async function handleRegenerateSingleSlide(event) {
  if (!currentPresentation) return;
  const slideNo = currentPresentation.slides[currentSlideIndex].slide_number;

  const btn = (event && event.currentTarget) || document.getElementById('btn-regen-slide');
  const originalText = btn ? btn.innerHTML : 'Regenerate Slide';
  if (btn) {
    btn.innerText = 'Regenerating Slide...';
    btn.disabled = true;
  }

  try {
    const res = await fetch('/regenerate-slide', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        presentation_id: currentPresentation.id,
        slide_number: slideNo,
      }),
    });

    if (res.ok) {
      const updatedSlide = await res.json();
      currentPresentation.slides[currentSlideIndex] = updatedSlide;
      saveToHistory(currentPresentation);
      renderCurrentSlideDetail();
      renderGeneratedPresentation(currentPresentation);
    } else {
      alert('Slide regeneration failed.');
    }
  } catch (e) {
    alert('Regeneration error: ' + e.message);
  } finally {
    if (btn) {
      btn.innerHTML = originalText;
      btn.disabled = false;
    }
  }
}

async function handleRefineCurrent(event) {
  if (!currentPresentation) return;
  const btn = (event && event.currentTarget) || document.getElementById('btn-refine-outline');
  const originalHtml = btn ? btn.innerHTML : 'Refine Redundancy';
  if (btn) {
    btn.innerText = 'Refining Content...';
    btn.disabled = true;
  }

  try {
    const res = await fetch('/refine', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ presentation_id: currentPresentation.id }),
    });

    if (res.ok) {
      currentPresentation = await res.json();
      saveToHistory(currentPresentation);
      renderGeneratedPresentation(currentPresentation);
      alert(`Semantic refinement completed. Redundant points refined: ${currentPresentation.points_refined}`);
    }
  } catch (e) {
    alert('Refine error: ' + e.message);
  } finally {
    if (btn) {
      btn.innerHTML = originalHtml;
      btn.disabled = false;
    }
  }
}

// ==========================================================================
// Screen 6: Export System (PPTX / MD / JSON)
// ==========================================================================
function openExportModal() {
  if (!currentPresentation) {
    alert('Please select or generate a presentation first.');
    return;
  }
  document.getElementById('export-modal').classList.add('active');
}

function closeExportModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.classList.contains('modal-close-btn')) return;
  document.getElementById('export-modal').classList.remove('active');
}

async function triggerDownload(format) {
  if (!currentPresentation) return;

  const endpoint = `/export/${format}`;
  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(currentPresentation),
    });

    if (!res.ok) throw new Error(`Export to ${format} failed`);

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const ext = format === 'pptx' ? 'pptx' : (format === 'markdown' ? 'md' : 'json');
    const safeTopic = (currentPresentation.topic || 'presentation').replace(/[^a-zA-Z0-9_-]/g, '_');
    a.download = `PresentAI_${safeTopic}.${ext}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error('Download error:', err);
    alert(`Export error: ${err.message}`);
  }
}

// ==========================================================================
// Screen 7: My Presentations (History & Persistence)
// ==========================================================================
function seedInitialHistory() {
  try {
    let list = getHistoryList();
    if (!list || list.length === 0) {
      list = [getHealthcareDemoData(), getAutonomousDrivingDemoData()];
      localStorage.setItem('ai_pres_history', JSON.stringify(list));
    }
  } catch (e) {
    console.warn('Seeding error:', e);
  }
}

function saveToHistory(presentation) {
  try {
    const list = getHistoryList();
    const existingIdx = list.findIndex(p => p.id === presentation.id);
    if (existingIdx >= 0) {
      list[existingIdx] = presentation;
    } else {
      list.unshift(presentation);
    }
    localStorage.setItem('ai_pres_history', JSON.stringify(list.slice(0, 30)));
    renderHistoryCards();
  } catch (e) {
    console.warn('LocalStorage save error:', e);
  }
}

function getHistoryList() {
  try {
    const str = localStorage.getItem('ai_pres_history');
    return str ? JSON.parse(str) : [];
  } catch (e) {
    return [];
  }
}

function setHistoryFilter(filterName) {
  currentFilter = filterName;
  document.querySelectorAll('#history-filter-pills .filter-pill').forEach(pill => {
    pill.classList.toggle('active', pill.innerText.includes(filterName));
  });
  renderHistoryCards();
}

function renderHistoryCards() {
  const container = document.getElementById('history-cards-grid');
  if (!container) return;

  const search = (document.getElementById('history-search-input')?.value || '').toLowerCase();
  let list = getHistoryList();

  if (list.length === 0) {
    list = [getHealthcareDemoData(), getAutonomousDrivingDemoData()];
    localStorage.setItem('ai_pres_history', JSON.stringify(list));
  }

  const filtered = list.filter(item => {
    const matchesSearch = item.topic.toLowerCase().includes(search) || (item.objective || '').toLowerCase().includes(search);
    if (!matchesSearch) return false;
    if (currentFilter === 'All' || currentFilter === 'Recent') return true;
    return item.presentation_type === currentFilter;
  });

  if (filtered.length === 0) {
    container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 40px;">No presentations match your search.</div>`;
    return;
  }

  container.innerHTML = filtered.map(item => `
    <div class="history-card">
      <div>
        <div class="hcard-header">
          <span class="badge-pill" style="font-size: 0.65rem; padding: 2px 8px;">${escapeHtml(item.domain || 'Technology')}</span>
          <span class="hcard-date">${escapeHtml(item.created_at || 'Ready')}</span>
        </div>
        <h3 class="hcard-title">${escapeHtml(item.topic)}</h3>
        <div class="hcard-meta">
          <span class="hcard-pill">${item.num_slides} Slides</span>
          <span class="hcard-pill">${item.duration} Mins</span>
          <span class="hcard-pill">${escapeHtml(item.audience || 'General')}</span>
          <span class="hcard-pill">${escapeHtml(item.difficulty || 'Intermediate')}</span>
        </div>
      </div>
      <div class="hcard-actions">
        <button class="btn btn-secondary btn-sm" onclick="openFromHistory('${item.id}')">Open</button>
        <button class="btn btn-secondary btn-sm" onclick="exportFromHistory('${item.id}')">Export</button>
        <button class="btn btn-secondary btn-sm" style="color: var(--danger);" onclick="deleteFromHistory('${item.id}')">Delete</button>
      </div>
    </div>
  `).join('');
}

function openFromHistory(presId) {
  const list = getHistoryList();
  const pres = list.find(p => p.id === presId);
  if (pres) {
    currentPresentation = pres;
    renderGeneratedPresentation(pres);
    navigateTo('result');
  }
}

function exportFromHistory(presId) {
  const list = getHistoryList();
  const pres = list.find(p => p.id === presId);
  if (pres) {
    currentPresentation = pres;
    openExportModal();
  }
}

function deleteFromHistory(presId) {
  const list = getHistoryList().filter(p => p.id !== presId);
  localStorage.setItem('ai_pres_history', JSON.stringify(list));
  renderHistoryCards();
}

// ==========================================================================
// PRE-DEFINED DEMOS (Two Fully-Developed Featured Presentations)
// ==========================================================================
function loadDemoPresentation(demoType) {
  const demoData = demoType === 'autonomous_driving'
    ? getAutonomousDrivingDemoData()
    : getHealthcareDemoData();

  currentPresentation = demoData;
  saveToHistory(demoData);
  renderGeneratedPresentation(demoData);
  navigateTo('result');
}

// Demo 1: Healthcare (8 Slides)
function getHealthcareDemoData() {
  return {
    id: "pres_demo_healthcare",
    topic: "Artificial Intelligence in Healthcare",
    objective: "Explain how AI is transforming healthcare diagnosis and patient care",
    audience: "College Students",
    difficulty: "Intermediate",
    presentation_type: "Technical Seminar",
    num_slides: 8,
    duration: 12,
    domain: "Healthcare",
    points_refined: 5,
    redundant_points_detected: 5,
    created_at: "Production Ready",
    slides: [
      {
        slide_number: 1,
        title: "Introduction to Artificial Intelligence in Healthcare",
        purpose: "Introduce the role and transformational potential of AI in modern clinical workflows.",
        time_minutes: 1.5,
        bullets: [
          "Overview and definition of artificial intelligence applied to clinical biomedical systems.",
          "Transition from rule-based medical expert systems to statistical deep learning representations.",
          "Major clinical domains: automated radiologic imaging, electronic health record intelligence, and oncology."
        ],
        case_study: "FDA approval of autonomous AI diagnostic devices for early diabetic retinopathy detection without ophthalmologist intervention.",
        speaker_notes: "Welcome the audience. Emphasize that AI in medicine acts as an assistive decision tool rather than a replacement for clinical judgment."
      },
      {
        slide_number: 2,
        title: "Evolution and Background of Healthcare AI",
        purpose: "Examine historical milestones leading to modern clinical transformers.",
        time_minutes: 1.5,
        bullets: [
          "Early expert systems like MYCIN and rule-based diagnostic trees in clinical medicine.",
          "Advent of convolutional neural networks (CNNs) revolutionizing 2D and 3D medical image segmentation.",
          "Scaling laws and multimodal vision-language transformers synthesizing clinical text and imaging."
        ],
        case_study: "Stanford CheXNeXt model matching 11 practicing radiologists across 14 distinct chest radiograph pathologies.",
        speaker_notes: "Highlight how dataset availability (such as MIMIC and ImageNet) unlocked rapid breakthroughs over the past decade."
      },
      {
        slide_number: 3,
        title: "Core AI Technologies Used in Clinical Medicine",
        purpose: "Explain the principal deep learning architectures powering healthcare intelligence.",
        time_minutes: 1.5,
        bullets: [
          "3D Convolutional Neural Networks and U-Net architectures for volumetric organ segmentation.",
          "Biomedical Transformer Language Models (BioBERT, ClinicalBERT) for automated pathology report parsing.",
          "Graph Neural Networks modeling molecular protein structures and biochemical drug interactions."
        ],
        case_study: "DeepMind AlphaFold resolving the 3D structure of over 200 million cataloged proteins, compressing decades of wet-lab research.",
        speaker_notes: "Clarify the difference between vision networks for CT/MRI scans and language models for unstructured clinical progress notes."
      },
      {
        slide_number: 4,
        title: "AI-Based Medical Diagnosis and Pathology",
        purpose: "Analyze computer-aided detection and real-time clinical screening pipelines.",
        time_minutes: 1.5,
        bullets: [
          "Computer-aided detection algorithms screening high-resolution digital mammography.",
          "Automated lesion identification and boundary delimitation in digital pathology whole-slide images.",
          "Risk stratification algorithms flagging imminent hemodynamic instability in intensive care units."
        ],
        case_study: "Johns Hopkins hospital deployment of machine learning early-warning algorithms reducing sepsis patient mortality by 18.2%.",
        speaker_notes: "Explain to the audience that early triage in emergency departments saves lives by directing specialist attention where most critical."
      },
      {
        slide_number: 5,
        title: "Real-World Healthcare Applications",
        purpose: "Demonstrate applied clinical operations, remote monitoring, and workflow optimization.",
        time_minutes: 1.5,
        bullets: [
          "Continuous wearable sensor monitoring detecting cardiac arrhythmias and atrial fibrillation episodes.",
          "Generative ambient clinical documentation synthesizing physician-patient dialogues into structured EHR entries.",
          "Robotic surgical assistance offering sub-millimeter instrument guidance and tremor suppression."
        ],
        case_study: "Epic Systems ambient listening copilot eliminating 1.5 hours of physician administrative charting per clinical shift.",
        speaker_notes: "Point out that physician burnout is directly mitigated through intelligent transcription and documentation automation."
      },
      {
        slide_number: 6,
        title: "System Benefits and Critical Implementation Challenges",
        purpose: "Critically evaluate clinical advantages alongside privacy, bias, and regulatory bottlenecks.",
        time_minutes: 1.5,
        bullets: [
          "Quantifiable benefits: reduced diagnostic latency, triage accuracy, and equalized access in underserved regions.",
          "Critical challenges: dataset bias, lack of out-of-distribution model robustness, and adversarial noise sensitivity.",
          "Privacy and governance: HIPAA compliance, patient consent protocols, and European AI Act high-risk classifications."
        ],
        case_study: "Empirical study revealing diagnostic performance degradation when skin lesion algorithms were tested across diverse under-represented skin tones.",
        speaker_notes: "Highlight that algorithm fairness and representative training data are vital for equitable patient health outcomes."
      },
      {
        slide_number: 7,
        title: "Future Horizons and Emerging AI Paradigms",
        purpose: "Explore next-generation frontiers in personalized genomics and federated health networks.",
        time_minutes: 1.5,
        bullets: [
          "Federated learning paradigms training global biomedical models across hospitals without transmitting sensitive patient records.",
          "Precision medicine algorithms mapping single-cell RNA sequencing data to personalized oncology therapies.",
          "Multimodal foundation models providing unified interactive reasoning across imaging, lab panels, and clinical histories."
        ],
        case_study: "Consortium of 20 cancer centers across Europe training federated glioma segmentation models preserving GDPR patient privacy.",
        speaker_notes: "Discuss how federated learning overcomes the legal and institutional barriers to sharing sensitive health records."
      },
      {
        slide_number: 8,
        title: "Conclusion and Strategic Summary",
        purpose: "Synthesize key insights and establish future principles for human-in-the-loop AI integration.",
        time_minutes: 1.5,
        bullets: [
          "AI serves as an indispensable cognitive amplifier for physicians, not an autonomous clinician substitute.",
          "Rigorous prospective randomized clinical trials are required before wide-scale hospital algorithm deployment.",
          "Interdisciplinary synergy between machine learning engineers and clinicians is essential for meaningful impact."
        ],
        case_study: "AMA position paper formalizing 'Augmented Intelligence' as the collaborative future standard for healthcare technology.",
        speaker_notes: "Conclude by summarizing the core message: the most effective healthcare systems combine human empathy with machine precision."
      }
    ]
  };
}

// Demo 2: Autonomous Driving & Computer Vision (10 Slides)
function getAutonomousDrivingDemoData() {
  return {
    id: "pres_demo_autonomous_driving",
    topic: "Autonomous Driving and Computer Vision",
    objective: "Analyze deep neural perception, LiDAR sensor fusion, and real-time path planning in self-driving vehicles",
    audience: "Engineering Faculty",
    difficulty: "Advanced",
    presentation_type: "Technical Seminar",
    num_slides: 10,
    duration: 15,
    domain: "Deep Learning / Technology",
    points_refined: 4,
    redundant_points_detected: 4,
    created_at: "Production Ready",
    slides: [
      {
        slide_number: 1,
        title: "Introduction to Autonomous Driving and Computer Vision",
        purpose: "Introduce foundational autonomy taxonomy, operational design domains, and perception pipelines.",
        time_minutes: 1.5,
        bullets: [
          "SAE Level 0 to Level 5 autonomy spectrum and real-time compute requirements.",
          "Decomposition of autonomy stack: perception, localization, state estimation, and path execution.",
          "Critical role of convolutional and transformer backbones operating on 360-degree camera feeds."
        ],
        case_study: "Waymo commercial robotaxi deployment accumulating over 20 million driverless commercial miles with safety benchmark parity.",
        speaker_notes: "Introduce the seminar scope covering edge computer vision, multimodal sensor fusion, and latency bounds for autonomous systems."
      },
      {
        slide_number: 2,
        title: "Sensor Modalities & Multi-Modal Perception",
        purpose: "Examine complementary physical sensor characteristics and signal acquisition.",
        time_minutes: 1.5,
        bullets: [
          "High-resolution CMOS image sensors providing dense RGB texture and semantic sign identification.",
          "Frequency-modulated continuous-wave (FMCW) LiDAR yielding direct 3D point cloud coordinate geometries.",
          "Millimeter-wave radar providing all-weather Doppler velocity measurements and obstruction penetration."
        ],
        case_study: "Comparative evaluation of Tesla camera-only vision approach vs. Waymo heterogeneous LiDAR-radar-vision architecture in adverse fog.",
        speaker_notes: "Explain trade-offs between dense semantic texture from RGB cameras and precise metric depth from rotating LiDAR scanners."
      },
      {
        slide_number: 3,
        title: "Deep Neural Perception & 3D Object Detection",
        purpose: "Break down state-of-the-art vision architectures mapping raw sensors to bounding boxes.",
        time_minutes: 1.5,
        bullets: [
          "Bird's-Eye-View (BEV) perception transformers projecting multi-camera perspective images into unified ground planes.",
          "PointNet and VoxelNet neural architectures directly processing sparse unstructured 3D LiDAR point clouds.",
          "Simultaneous multi-task networks outputting 3D bounding boxes, semantic lane topologies, and road drivability masks."
        ],
        case_study: "BEVFormer spatial-temporal cross-attention architecture outperforming prior LiDAR baselines by 4.2 points on the nuScenes benchmark.",
        speaker_notes: "Point out how transformer cross-attention mechanisms seamlessly resolve camera perspective depth ambiguities into top-down representations."
      },
      {
        slide_number: 4,
        title: "Sensor Fusion Architectures: Early vs. Late Fusion",
        purpose: "Analyze mathematical representations for combining disparate sensor streams.",
        time_minutes: 1.5,
        bullets: [
          "Early fusion combining raw calibrated camera pixels and projected LiDAR depth maps prior to feature extraction.",
          "Late fusion consolidating high-level candidate object detections via Bayesian Kalman filtering.",
          "Deep middle fusion utilizing transformer attention to exchange cross-modal feature embeddings dynamically."
        ],
        case_study: "Deployment of middle-fusion architecture on NVIDIA DRIVE Orin compute platforms achieving 30 FPS deterministic inference.",
        speaker_notes: "Walk the audience through the trade-offs: early fusion is information-rich but sensitive to calibration jitter; late fusion is robust but discards weak signal synergy."
      },
      {
        slide_number: 5,
        title: "Simultaneous Localization and Mapping (SLAM)",
        purpose: "Examine high-definition spatial mapping and centimeter-accurate vehicle positioning.",
        time_minutes: 1.5,
        bullets: [
          "Visual-Inertial Odometry (VIO) coupling feature tracking with high-frequency IMU accelerometer updates.",
          "HD map vector representations encoding centimeter-precision lane boundaries, intersection rules, and signal heads.",
          "LiDAR scan matching against pre-built surfel maps maintaining localization in GNSS-denied environments."
        ],
        case_study: "Centimeter-accurate localization sustained through GPS-denied highway tunnels using LiDAR point cloud normal distribution transforms.",
        speaker_notes: "Detail how urban street canyons cause GNSS multipath errors, necessitating point-cloud scan matching against pre-computed HD maps."
      },
      {
        slide_number: 6,
        title: "Motion Prediction & Agent Trajectory Forecasting",
        purpose: "Analyze probabilistic trajectory forecasting for surrounding dynamic agents.",
        time_minutes: 1.5,
        bullets: [
          "Recurrent graph neural networks modeling interactive lane-vehicle and vehicle-pedestrian spatio-temporal dynamics.",
          "Multi-modal trajectory distributions capturing divergent intention hypotheses (e.g. yield vs. turn).",
          "Social pooling mechanisms modeling cooperative multi-agent interactions at complex four-way intersections."
        ],
        case_study: "Waymo TNT (Target-driven Trajectory Prediction) accurately predicting erratic pedestrian lane-crossing maneuvers 3 seconds prior to divergence.",
        speaker_notes: "Emphasize that motion forecasting cannot produce a single deterministic line; it must output multi-modal Gaussian distributions over potential futures."
      },
      {
        slide_number: 7,
        title: "Path Planning, Behavioral Decision Making & Control",
        purpose: "Explore real-time trajectory optimization and collision avoidance controllers.",
        time_minutes: 1.5,
        bullets: [
          "Hierarchical motion planners splitting long-horizon mission routing from short-horizon collision avoidance.",
          "Model Predictive Control (MPC) optimizing vehicle steering angle, acceleration, and jerk boundaries.",
          "End-to-end neural motion planning models directly mapping sensor representations to trajectory waypoints."
        ],
        case_study: "Real-time non-linear Model Predictive Control executing evasive double-lane change maneuvers with zero tire slip saturation.",
        speaker_notes: "Contrast rule-based cost-function optimizers against emerging differentiable end-to-end driving models."
      },
      {
        slide_number: 8,
        title: "Edge Compute Hardware & Latency Budgets",
        purpose: "Examine embedded inference platforms, safety watchdogs, and deterministic execution.",
        time_minutes: 1.5,
        bullets: [
          "Automotive SoC architectures (NVIDIA Orin, Tesla FSD Chip) delivering 250+ INT8/FP16 Deep Learning TOPS.",
          "Strict 100-millisecond end-to-end latency budget from photon capture to actuator brake execution.",
          "ASIL-D safety integrity standards requiring redundant lockstep CPUs and independent fallback trajectory systems."
        ],
        case_study: "Dual-redundant automotive system architecture automatically isolating primary SoC thermal faults within 8 milliseconds.",
        speaker_notes: "Remind the faculty audience that a 100ms compute delay at 100 km/h corresponds to 2.8 meters of unguided vehicle displacement."
      },
      {
        slide_number: 9,
        title: "Edge Cases, OOD Scenarios & Safety Verification",
        purpose: "Analyze long-tail safety distribution and simulation validation paradigms.",
        time_minutes: 1.5,
        bullets: [
          "The long-tail distribution challenge: emergency vehicles, road debris, construction detours, and adverse glare.",
          "Out-of-distribution (OOD) neural uncertainty estimation quantifying model epistemic confidence.",
          "Photorealistic neural radiance field (NeRF) simulation running billions of virtual stress-test miles."
        ],
        case_study: "Generative world models synthesizing adversarial rain, blinding glare, and tumbling debris to validate vision robustness in simulation.",
        speaker_notes: "Explain that autonomous driving safety is dominated by the rare long-tail scenarios occurring once every million miles."
      },
      {
        slide_number: 10,
        title: "Conclusion & Next-Generation Autonomous Horizons",
        purpose: "Synthesize architectural principles and explore foundation models in autonomy.",
        time_minutes: 1.5,
        bullets: [
          "Convergence toward unified end-to-end foundation models connecting vision-language reasoning to vehicle actuation.",
          "Transition from HD-map dependent geofenced robotaxis to mapless generalized urban perception.",
          "Regulatory certification frameworks establishing ISO 26262 and SOTIF safety validation benchmarks worldwide."
        ],
        case_study: "Open-source benchmark initiatives standardizing autonomous vehicle safety validation protocols across international transport agencies.",
        speaker_notes: "Conclude the presentation by summarizing the ultimate goal: deploying verifiable, generalizable vision agents that eliminate preventable traffic fatalities."
      }
    ]
  };
}

// Utility: HTML Escaping
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}


// Keyboard Navigation for Detail Canvas Studio View (Left, Right, Escape)
document.addEventListener('keydown', (e) => {
  const detailScreen = document.getElementById('screen-detail');
  if (detailScreen && detailScreen.classList.contains('active')) {
    if (document.activeElement && (document.activeElement.isContentEditable || ['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName))) {
      return;
    }
    if (e.key === 'ArrowRight') {
      if (currentPresentation && currentSlideIndex < currentPresentation.slides.length - 1) {
        navigateSlide(1);
      }
    } else if (e.key === 'ArrowLeft') {
      if (currentSlideIndex > 0) {
        navigateSlide(-1);
      }
    } else if (e.key === 'Escape') {
      navigateTo('result');
    }
  }
});
