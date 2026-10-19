let scrollCount = 0;
let lastScroll = 0;
let scrollSpeed = 0;
let loadClicks = 0;

document.addEventListener("click", () => {

    const loaderVisible =
        document.getElementById("loader").style.display !== "none";

    if(loaderVisible){
        loadClicks++;
    }

});


window.addEventListener("scroll", () => {

    scrollCount++;

    let now = Date.now();

    if(lastScroll){
        scrollSpeed += 1000 / (now - lastScroll);
    }

    lastScroll = now;

});


setTimeout(() => {

    document.getElementById("loader").style.display = "none";
    document.getElementById("content").style.display = "block";

}, 10000);


function finishTest(){

    let quizScore =
        parseInt(document.getElementById("answer").value);

    fetch("/submit_metrics", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            scrollCount,
            scrollSpeed,
            loadClicks,
            quizScore
        })

    })
    .then(r => r.json())
    .then(data => {

        window.location =
            `/result?score=${data.score}`;

    });

}