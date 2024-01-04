var toggleButton = document.getElementById("navbar-toggle");
var mobileNavbar = document.getElementById("mobile-navbar");

toggleButton.addEventListener("click", function () {
  mobileNavbar.classList.toggle("hidden");
});

// document.querySelectorAll('a[href^="#"]').forEach(anchor => {
//     anchor.addEventListener('click', function (e) {
//         e.preventDefault();

//         const targetId = this.getAttribute('href').substring(1);
//         const targetElement = document.getElementById(targetId);

//         if (targetElement) {
//             targetElement.scrollIntoView({
//                 behavior: 'smooth'
//             });
//         }
//     });
// });
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();

      document.querySelector(this.getAttribute("href")).scrollIntoView({
        behavior: "smooth",
      });
    });
  });
});
function handleFilterDate(checkboxes, rows, col) {
  checkboxes.forEach(function (checkbox) {
    checkbox.addEventListener("change", function () {
      let checkboxChecked = false;
      checkboxes.forEach(function (checkbox) {
        const date = checkbox.id;
        const isChecked = checkbox.checked;

        if (isChecked) {
          checkboxChecked = true;
        }
        for (let i = 0; i < rows.length; i++) {
          const row = rows[i];
          const cellContent = row.cells[col].textContent;
          const today = new Date();
          const date_today = new Date(cellContent);
          const diffTime = Math.abs(today - date_today);
          if (date == "currentweek" && diffTime < 604800000) {
            row.style.display = isChecked ? "" : "none";
          } else if (
            date == "pastweek" &&
            diffTime > 604800000 &&
            diffTime < 1209600000
          ) {
            row.style.display = isChecked ? "" : "none";
          } else if (
            date == "2weeks" &&
            diffTime > 1209600000 &&
            diffTime < 2592000000
          ) {
            row.style.display = isChecked ? "" : "none";
          } else if (
            date == "1month" &&
            diffTime > 2592000000 &&
            diffTime < 7776000000
          ) {
            row.style.display = isChecked ? "" : "none";
          } else if (
            date == "90days" &&
            diffTime > 7776000000 &&
            diffTime < 7884000000
          ) {
            row.style.display = isChecked ? "" : "none";
          }
        }
      });

      if (!checkboxChecked) {
        for (let i = 0; i < rows.length; i++) {
          rows[i].style.display = "";
        }
      }
    });
  });
}

function handleFilter(checkboxes, rows, col) {
  checkboxes.forEach(function (checkbox) {
    checkbox.addEventListener("change", function () {
      let checkboxChecked = false;
      checkboxes.forEach(function (checkbox) {
        const filter = checkbox.id;
        const isChecked = checkbox.checked;

        if (isChecked) {
          checkboxChecked = true;
        }
        for (let i = 0; i < rows.length; i++) {
          const row = rows[i];
          if (row.cells[col].textContent.trim() === filter) {
            row.style.display = isChecked ? "" : "none";
          }
        }
      });

      if (!checkboxChecked) {
        for (let i = 0; i < rows.length; i++) {
          rows[i].style.display = "";
        }
      }
    });
  });
}

function searchListener(search, rows, col) {
  search.addEventListener("keyup", function () {
    const value = search.value.toLowerCase();
    for (let i = 1; i < rows.length; i++) {
      const row = rows[i];
      let rowContainsValue = false;

      for (let j = 0; j <= col; j++) {
        const cellContent = row.cells[j].textContent.toLowerCase();
        if (cellContent.includes(value)) {
          rowContainsValue = true;
          break;
        }
      }

      if (rowContainsValue) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    }
  });
}