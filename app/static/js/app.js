const COMPLETED_AT_KEY = "vocational_test_completed_at";
const RECENT_COMPLETION_WINDOW_MS = 24 * 60 * 60 * 1000;

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

markVocationalTestCompleted();
showRecentCompletionWarning();
