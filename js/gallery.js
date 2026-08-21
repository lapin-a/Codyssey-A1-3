// js/gallery.js
// 보관함 페이지: /api/get-characters 를 호출해서 저장된 캐릭터 카드 목록을 렌더링

document.addEventListener('DOMContentLoaded', () => {
  const galleryLoading = document.getElementById('galleryLoading');
  const galleryEmpty = document.getElementById('galleryEmpty');
  const galleryError = document.getElementById('galleryError');
  const galleryGrid = document.getElementById('galleryGrid');

  const REQUEST_TIMEOUT_MS = 15000;

  function showState(state) {
    // state: 'loading' | 'empty' | 'error' | 'grid'
    galleryLoading.hidden = state !== 'loading';
    galleryEmpty.hidden = state !== 'empty';
    galleryError.hidden = state !== 'error';
    galleryGrid.hidden = state !== 'grid';
  }

  function createCardElement(character) {
    const card = document.createElement('article');
    card.className = 'char-card';

    const metaParts = [character.gender, character.age, character.species, character.religion].filter(
      (v) => v && String(v).trim().length > 0
    );

    card.innerHTML = `
      <div class="char-card-tab"></div>
      <header class="char-card-head">
        <h2>${escapeHtml(character.name || '이름 없음')}</h2>
        <span class="char-card-genre">${escapeHtml(character.genre || '')}</span>
      </header>
      <p class="char-card-meta">${escapeHtml(metaParts.join(' · '))}</p>
      <dl class="char-card-body">
        ${
          character.extra_info
            ? `<div class="char-card-row">
                 <dt>추가 설정</dt>
                 <dd>${escapeHtml(character.extra_info)}</dd>
               </div>`
            : ''
        }
        <div class="char-card-row">
          <dt>성격</dt>
          <dd>${escapeHtml(character.personality || '-')}</dd>
        </div>
        <div class="char-card-row">
          <dt>말투 예시</dt>
          <dd>${escapeHtml(character.speech_style || '-')}</dd>
        </div>
        <div class="char-card-row">
          <dt>배경 이야기</dt>
          <dd>${escapeHtml(character.backstory || '-')}</dd>
        </div>
        <div class="char-card-row char-card-row--split">
          <div>
            <dt>강점</dt>
            <dd>${escapeHtml(character.strengths || '-')}</dd>
          </div>
          <div>
            <dt>약점</dt>
            <dd>${escapeHtml(character.weaknesses || '-')}</dd>
          </div>
        </div>
      </dl>
    `;
    return card;
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  async function loadCharacters() {
    showState('loading');

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
      const response = await fetch(`/api/get-characters?client_id=${encodeURIComponent(window.getClientId())}`, {
        signal: controller.signal,
      });
      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || '캐릭터를 불러오는 중 오류가 발생했습니다.');
      }

      const characters = data.result || [];

      if (characters.length === 0) {
        showState('empty');
        return;
      }

      galleryGrid.innerHTML = '';
      characters.forEach((character) => {
        galleryGrid.appendChild(createCardElement(character));
      });
      showState('grid');
    } catch (err) {
      showState('error');
    } finally {
      clearTimeout(timeoutId);
    }
  }

  loadCharacters();
});