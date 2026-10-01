// MODAL
function openModal() {
  document.getElementById("modal").style.display = "block";
}

function closeModal() {
  document.getElementById("modal").style.display = "none";
}

// FAVOURITE ❤️
function toggleFav(el) {
  if (el.innerText === "♡") {
    el.innerText = "❤️";
  } else {
    el.innerText = "♡";
  }
}

let slides = document.querySelectorAll(".slide");
let index = 0;

function showSlide(i) {
  slides.forEach(s => s.classList.remove("active"));
  slides[i].classList.add("active");
}

function nextSlide() {
  index = (index + 1) % slides.length;
  showSlide(index);
}

function prevSlide() {
  index = (index - 1 + slides.length) % slides.length;
  showSlide(index);
}

setInterval(nextSlide, 3000);

// INITIAL LOAD
showSlide(index);