document.getElementById("file-form").addEventListener("submit", function (e) {
  var fileInput = document.getElementById("file-input");
  if (!fileInput.value) {
    e.preventDefault();
    alert("Please select a file!");
  }
});
