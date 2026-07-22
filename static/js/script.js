document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("scheme-form");
  if (!form) return;

  const submitBtn = document.getElementById("submit-btn");
  const spinner = document.getElementById("submit-spinner");
  const label = document.getElementById("submit-label");
  const resetBtn = document.getElementById("reset-btn");
  const ageField = document.getElementById("age");
  const seniorCitizenField = document.getElementById("senior_citizen");
  const maritalStatusField = document.getElementById("marital_status");
  const pregnantFieldWrapper = document.getElementById("pregnant-field-wrapper");
  const pregnantField = document.getElementById("pregnant");

  function syncSeniorCitizen() {
    if (!ageField || !seniorCitizenField) return;

    const ageValue = Number(ageField.value);
    if (!Number.isNaN(ageValue) && ageValue > 0) {
      seniorCitizenField.value = ageValue >= 60 ? "Yes" : "No";
    } else {
      seniorCitizenField.value = "No";
    }
  }

  function togglePregnantField() {
    if (!pregnantFieldWrapper || !pregnantField || !maritalStatusField) return;

    const isMarried = maritalStatusField.value === "Married";
    if (isMarried) {
      pregnantFieldWrapper.style.display = "block";
      pregnantFieldWrapper.style.opacity = "1";
      pregnantFieldWrapper.style.transform = "translateY(0)";
    } else {
      pregnantField.value = "No";
      pregnantFieldWrapper.style.opacity = "0";
      pregnantFieldWrapper.style.transform = "translateY(-4px)";
      window.setTimeout(function () {
        if (pregnantFieldWrapper.style.opacity === "0") {
          pregnantFieldWrapper.style.display = "none";
        }
      }, 180);
    }
  }

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

  if (ageField) {
    ageField.addEventListener("input", syncSeniorCitizen);
    ageField.addEventListener("change", syncSeniorCitizen);
  }

  if (maritalStatusField) {
    maritalStatusField.addEventListener("change", togglePregnantField);
  }

  syncSeniorCitizen();
  togglePregnantField();

  resetBtn.addEventListener("click", function () {
    form.querySelectorAll(".is-invalid, .is-valid").forEach(function (field) {
      field.classList.remove("is-invalid", "is-valid");
    });
    submitBtn.disabled = false;
    spinner.classList.add("d-none");
    label.textContent = "Predict Scheme";
    window.setTimeout(function () {
      syncSeniorCitizen();
      togglePregnantField();
    }, 0);
  });
});