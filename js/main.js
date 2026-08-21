// js/main.js
// 모든 페이지에서 공통으로 쓰이는 네비게이션 동작을 담당합니다.

// 로그인 없이 "내 캐릭터"를 구분하기 위해, 이 브라우저만의 고유 ID를 발급해서
// localStorage에 저장해둡니다. create.js, gallery.js에서 window.getClientId()로 사용합니다.
window.getClientId = function () {
  const STORAGE_KEY = 'chartcoto_client_id';
  let clientId = localStorage.getItem(STORAGE_KEY);
  if (!clientId) {
    clientId = (crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(36).slice(2)}`);
    localStorage.setItem(STORAGE_KEY, clientId);
  }
  return clientId;
};

document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.getElementById('navToggle');
  const mainNav = document.querySelector('.main-nav');

  if (!navToggle || !mainNav) return;

  navToggle.addEventListener('click', () => {
    const isOpen = mainNav.classList.toggle('is-open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
  });

  // 메뉴 항목을 클릭하면(페이지 이동 전) 모바일 메뉴를 닫아줍니다.
  mainNav.querySelectorAll('.nav-tab').forEach((tab) => {
    tab.addEventListener('click', () => {
      mainNav.classList.remove('is-open');
      navToggle.setAttribute('aria-expanded', 'false');
    });
  });

  // 화면을 태블릿 이상 크기로 넓히면 모바일 메뉴 상태를 초기화합니다.
  window.addEventListener('resize', () => {
    if (window.innerWidth >= 768) {
      mainNav.classList.remove('is-open');
      navToggle.setAttribute('aria-expanded', 'false');
    }
  });
});