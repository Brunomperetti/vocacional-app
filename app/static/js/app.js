const COMPLETED_AT_KEY = "vocational_test_completed_at";
const RECENT_COMPLETION_WINDOW_MS = 24 * 60 * 60 * 1000;

const META_EVENT_NAMES = {
  view_landing: "ViewLanding",
  start_test: "StartTest",
  test_step_view: "TestStepView",
  complete_test: "CompleteTest",
  download_pdf: "DownloadPDF",
  share_whatsapp: "ShareWhatsApp",
  donation_click: "DonationClick",
};

function trackEvent(eventName, params = {}) {
  try {
    if (typeof window.gtag === "function") {
      window.gtag("event", eventName, params);
    }

    if (typeof window.fbq === "function") {
      window.fbq("trackCustom", META_EVENT_NAMES[eventName] || eventName, params);
    }
  } catch (error) {
    console.info("No se pudo registrar el evento de medición.", error);
  }
}

function trackPageViewEvents() {
  const { page, isDemo, stepNumber, stepDimension } = document.body.dataset;

  if (page === "landing") {
    trackEvent("view_landing");
  }

  if (page === "test_step") {
    trackEvent("test_step_view", {
      step_number: Number(stepNumber),
      dimension: stepDimension,
    });
  }

  if (page === "result" && isDemo !== "true") {
    trackEvent("complete_test");
  }
}

function bindTrackedActions() {
  document.querySelectorAll("[data-track]").forEach((element) => {
    element.addEventListener("click", () => {
      trackEvent(element.dataset.track);
    });
  });
}

function markVocationalTestCompleted() {
  if (!window.vocacionalResultCompleted) return;

  try {
    window.localStorage.setItem(COMPLETED_AT_KEY, new Date().toISOString());
  } catch (error) {
    console.info("No se pudo guardar la fecha de finalización del test.", error);
  }
}

function showRecentCompletionWarning() {
  const warning = document.querySelector("[data-recent-test-warning]");
  if (!warning) return;

  try {
    const completedAt = window.localStorage.getItem(COMPLETED_AT_KEY);
    if (!completedAt) return;

    const completedAtTime = new Date(completedAt).getTime();
    if (Number.isNaN(completedAtTime)) return;

    const completedRecently = Date.now() - completedAtTime < RECENT_COMPLETION_WINDOW_MS;
    if (completedRecently) {
      warning.hidden = false;
    }
  } catch (error) {
    console.info("No se pudo revisar la fecha de finalización del test.", error);
  }
}

trackPageViewEvents();
bindTrackedActions();
markVocationalTestCompleted();
showRecentCompletionWarning();
