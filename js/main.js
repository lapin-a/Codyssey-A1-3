// js/main.js
// 모든 페이지에서 공통으로 쓰이는 네비게이션 동작을 담당합니다.

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