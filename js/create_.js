// js/create.js 
// 캐릭터 만들기 페이지: 입력 검증 -> /api/generate-character 호출
// -> 결과 표시 -> /api/save-character 로 저장

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('charForm');
  const nameInput = document.getElementById('charName');
  const genderSelect = document.getElementById('charGender');
  const ageInput = document.getElementById('charAge');
  const speciesInput = document.getElementById('charSpecies');
  const religionInput = document.getElementById('charReligion');
  const genreSelect = document.getElementById('charGenre');
  const keywordsInput = document.getElementById('charKeywords');
  const extraInput = document.getElementById('charExtra');
  const formError = document.getElementById('formError');

  const generateBtn = document.getElementById('generateBtn');
  const regenerateBtn = document.getElementById('regenerateBtn');
  const saveBtn = document.getElementById('saveBtn');
  const saveStatus = document.getElementById('saveStatus');

  const resultEmpty = document.getElementById('resultEmpty');
  const resultLoading = document.getElementById('resultLoading');
  const loadingText = document.getElementById('loadingText');
  const resultCard = document.getElementById('resultCard');

  const REQUEST_TIMEOUT_MS = 20000; // 20초
  const SLOW_RESPONSE_NOTICE_MS = 6000; // 6초 넘게 걸리면 안내 문구 교체

  let currentCharacter = null; // 최근 생성 결과 (저장/재생성용)
  let lastPayload = null; // 마지막으로 제출한 입력값 (사용자가 적은 추가 정보 보존용)

  function showState(state) {
    // state: 'empty' | 'loading' | 'result'
    resultEmpty.hidden = state !== 'empty';
    resultLoading.hidden = state !== 'loading';
    resultCard.hidden = state !== 'result';
  }

  function setFormError(message) {
    if (!message) {
      formError.hidden = true;
      formError.textContent = '';
      return;
    }
    formError.hidden = false;
    formError.textContent = message;
  }

  function validateInput() {
    const values = [
      nameInput.value,
      genderSelect.value,
      ageInput.value,
      speciesInput.value,
      religionInput.value,
      genreSelect.value,
      keywordsInput.value,
      extraInput.value,
    ];
    const hasAnyInput = values.some((v) => v.trim().length > 0);

    if (!hasAnyInput) {
      return '입력 내용을 확인해주세요. 최소 1개 이상의 항목을 입력해주세요.';
    }
    return null;
  }

  function fillResultCard(data) {
    document.getElementById('rcName').textContent = data.name || '이름 없음';
    document.getElementById('rcGenre').textContent = data.genre || '';

    const metaParts = [data.gender, data.age, data.species, data.religion].filter(
      (v) => v && String(v).trim().length > 0
    );
    document.getElementById('rcMeta').textContent = metaParts.join(' · ');

    const extraRow = document.getElementById('rcExtraRow');
    if (data.extra_info) {
      extraRow.hidden = false;
      document.getElementById('rcExtra').textContent = data.extra_info;
    } else {
      extraRow.hidden = true;
    }

    document.getElementById('rcPersonality').textContent = data.personality || '-';
    document.getElementById('rcSpeech').textContent = data.speech_style || '-';
    document.getElementById('rcBackstory').textContent = data.backstory || '-';
    document.getElementById('rcStrengths').textContent = data.strengths || '-';
    document.getElementById('rcWeaknesses').textContent = data.weaknesses || '-';
    document.getElementById('rcLikes').textContent = data.likes || '-';
    document.getElementById('rcDislikes').textContent = data.dislikes || '-';
  }

  async function generateCharacter() {
    const errorMsg = validateInput();
    if (errorMsg) {
      setFormError(errorMsg);
      return;
    }
    setFormError(null);

    const payload = {
      name: nameInput.value.trim(),
      gender: genderSelect.value,
      age: ageInput.value.trim(),
      species: speciesInput.value.trim(),
      religion: religionInput.value.trim(),
      genre: genreSelect.value,
      keywords: keywordsInput.value.trim(),
      extra_info: extraInput.value.trim(),
    };
    lastPayload = payload;

    showState('loading');
    loadingText.textContent = 'AI가 캐릭터를 만들고 있습니다...';
    generateBtn.disabled = true;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    const slowNoticeId = setTimeout(() => {
      loadingText.textContent = '생각보다 오래 걸리고 있어요. 조금만 더 기다려주세요...';
    }, SLOW_RESPONSE_NOTICE_MS);

    try {
      const response = await fetch('/api/generate-character', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'AI 요청 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
      }

      currentCharacter = { ...data.result, extra_info: payload.extra_info };
      fillResultCard(currentCharacter);
      saveStatus.hidden = true;
      showState('result');
    } catch (err) {
      let message = 'AI 요청 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
      if (err.name === 'AbortError') {
        message = '응답 시간이 초과되었습니다. 다시 시도해주세요.';
      } else if (err.message) {
        message = err.message;
      }
      setFormError(message);
      showState('empty');
    } finally {
      clearTimeout(timeoutId);
      clearTimeout(slowNoticeId);
      generateBtn.disabled = false;
    }
  }

  async function saveCharacter() {
    if (!currentCharacter) return;

    saveBtn.disabled = true;
    saveStatus.hidden = false;
    saveStatus.classList.remove('is-error');
    saveStatus.textContent = '저장하는 중...';

    try {
      const response = await fetch('/api/save-character', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentCharacter),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || '저장 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
      }

      saveStatus.textContent = '보관함에 저장했습니다.';
    } catch (err) {
      saveStatus.classList.add('is-error');
      saveStatus.textContent = err.message || '저장 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
    } finally {
      saveBtn.disabled = false;
    }
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    generateCharacter();
  });

  regenerateBtn.addEventListener('click', () => {
    generateCharacter();
  });

  saveBtn.addEventListener('click', () => {
    saveCharacter();
  });
});