const surveys = document.querySelectorAll(".survey-button");

for (let survey of surveys) {
  survey.addEventListener("click", function redirect_to_survey() {
    window.location.href = `${survey.id}/survey-setup`;
  });
}
