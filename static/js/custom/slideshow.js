// Next/previous controls
function plusSlides(n) {
    showSlides(slideIndex += n);
}

// Thumbnail image controls
function currentSlide(n) {
showSlides(slideIndex = n);
}

function showSlides(n) {
    var i;
    var slides = document.getElementsByClassName("mySlides");
    var dots = document.getElementsByClassName("demo");
    //var captionText = document.getElementById("caption");
    if (slides.length == 0){
        $("#slideshow_container").hide()
        return
    }else{
        $("#slideshow_container").show()
    }
    if (n > slides.length) {slideIndex = 1}
    if (n < 1) {slideIndex = slides.length}
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    for (i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" active", "");
    }
    slides[slideIndex-1].style.display = "block";
    dots[slideIndex-1].className += " active";
    //captionText.innerHTML = dots[slideIndex-1].alt;
} 


$(document).keydown(function(e){
    if (e.which == 37) { 
        if ($("#prev_btn").is(":visible")){
            plusSlides(-1)
            return false;
        }
    }
    if (e.which == 39) { 
        if ($("#next_btn").is(":visible")){
            plusSlides(1)
            return false;
        }
    }
});


$(document).ready( function () {
    if ($("#slideshow_container").length >0){
        window.slideIndex = 1
        if (("#slideshow_container").length){
            showSlides(slideIndex);
        }
    }
})
