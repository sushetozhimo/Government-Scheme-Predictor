document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("scheme-form");
  if (!form) return;

  const submitBtn = document.getElementById("submit-btn");
  const spinner = document.getElementById("submit-spinner");
  const label = document.getElementById("submit-label");
  const resetBtn = document.getElementById("reset-btn");

  function validateField(field) {
    let valid = field.checkValidity();

    // Extra rules beyond native HTML validation
    if (field.id === "age" && field.value !== "") {
      valid = valid && Number(field.value) > 0;
    }
    if (field.id === "annual_income" && field.value !== "") {
      valid = valid && Number(field.value) >= 0;
    }

    field.classList.toggle("is-invalid", !valid);
    field.classList.toggle("is-valid", valid && field.value !== "");
    return valid;
  }

  form.addEventListener("submit", function (event) {
    let formValid = true;

    form.querySelectorAll("input[required], select[required]").forEach(function (field) {
      if (!validateField(field)) {
        formValid = false;
      }
    });

    if (!formValid) {
      event.preventDefault();
      event.stopPropagation();
      return;
    }

    // Show loading spinner while the request is in flight
    submitBtn.disabled = true;
    spinner.classList.remove("d-none");
    label.textContent = "Predicting...";
  });

  form.querySelectorAll("input, select").forEach(function (field) {
    field.addEventListener("blur", function () {
      validateField(field);
    });
  });

  resetBtn.addEventListener("click", function () {
    form.querySelectorAll(".is-invalid, .is-valid").forEach(function (field) {
      field.classList.remove("is-invalid", "is-valid");
    });
    submitBtn.disabled = false;
    spinner.classList.add("d-none");
    label.textContent = "Predict Scheme";
  });
});