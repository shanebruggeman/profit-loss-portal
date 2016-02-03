$(document).ready(function() {

// Get the template HTML and remove it from the document template HTML and remove it from the doument
var previewNode = document.querySelector("#template");
previewNode.id = "";
var previewTemplate = previewNode.parentNode.innerHTML;
previewNode.parentNode.removeChild(previewNode);

var myDropzone = new Dropzone(document.body, { // Make the whole body a dropzone
  url: "/upload", // Set the url
  thumbnailWidth: 80,
  thumbnailHeight: 80,
  parallelUploads: 20,
  previewTemplate: previewTemplate,
  autoQueue: false, // Make sure the files aren't queued until manually added
  previewsContainer: "#previews", // Define the container to display the previews
  clickable: "#submit-files" // Define the element that should be used as click trigger to select files.
});

myDropzone.on("addedfile", function(file) {
  // Hookup the start button
  file.previewElement.querySelector(".start").onclick = function() { myDropzone.enqueueFile(file); };
});

myDropzone.on("success", function(file) {
  // Hookup the start button
  file.previewElement.querySelector("#progress-message").innerHTML = "Success";
});

myDropzone.on("sending", function(file, xhr, formData) {
  // And disable the start button
  file.previewElement.querySelector(".start").setAttribute("disabled", "disabled");
  acctid = $("option[name='account']:checked").val()
  formData.append("account", acctid);
});

});