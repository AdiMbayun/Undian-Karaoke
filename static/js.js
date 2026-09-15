let daftarLagu = [];
let laguTersedia = [];
let laguSudahKeluar = [];


// ================================
// LOAD DATA LAGU
// ================================

async function loadSongs() {

    try {

        const response = await fetch("/api/lagu");

        daftarLagu = await response.json();

        laguTersedia = [...daftarLagu];

        console.log("Jumlah lagu:", daftarLagu.length);

    } catch (error) {

        console.error("Gagal mengambil data lagu:", error);

        document.getElementById("status").innerText =
            "GAGAL MEMUAT DATA LAGU";

    }

}


// ================================
// UNDI LAGU
// ================================

function undianLagu() {

    if (laguTersedia.length === 0) {

        alert("Semua lagu sudah terundi!");

        return;
    }


    const button = document.getElementById("drawButton");

    button.disabled = true;


    const status = document.getElementById("status");

    const judul = document.getElementById("judul");

    const penyanyi = document.getElementById("penyanyi");


    status.innerText = "🎲 MENGUNDI...";

    judul.innerText = "???";

    penyanyi.innerText = "";


    // Animasi pengundian

    let counter = 0;

    const interval = setInterval(() => {

        const randomTemp =
            laguTersedia[
                Math.floor(Math.random() * laguTersedia.length)
            ];

        judul.innerText = randomTemp.judul;

        penyanyi.innerText = randomTemp.penyanyi;

        counter++;

        if (counter >= 15) {

            clearInterval(interval);

            tampilkanLagu();

        }

    }, 100);

}


// ================================
// PILIH LAGU FINAL
// ================================

function tampilkanLagu() {

    const randomIndex =
        Math.floor(Math.random() * laguTersedia.length);


    const lagu =
        laguTersedia[randomIndex];


    // Hapus dari lagu tersedia

    laguTersedia.splice(randomIndex, 1);


    // Simpan history

    laguSudahKeluar.push(lagu);


    // Tampilkan informasi

    const status =
        document.getElementById("status");

    const judul =
        document.getElementById("judul");

    const penyanyi =
        document.getElementById("penyanyi");


    status.innerText = "🎉 LAGU TERPILIH";

    judul.innerText = lagu.judul;

    penyanyi.innerText = lagu.penyanyi;


    // Animasi

    judul.classList.remove("animasi");

    void judul.offsetWidth;

    judul.classList.add("animasi");


    // ================================
    // PLAY VIDEO
    // ================================

    const video =
        document.getElementById("videoPlayer");


    video.src =
        "/static/videos/" +
        encodeURIComponent(lagu.video);


    video.load();


    video.play().catch(error => {

        console.log(
            "Autoplay membutuhkan interaksi user:",
            error
        );

    });


    // History

    updateHistory();


    document.getElementById("drawButton").disabled = false;

}


// ================================
// HISTORY
// ================================

function updateHistory() {

    const historyList =
        document.getElementById("historyList");


    historyList.innerHTML = "";


    laguSudahKeluar
        .slice()
        .reverse()
        .forEach((lagu, index) => {

            const div =
                document.createElement("div");


            div.className = "history-item";


            div.innerHTML =
                `${laguSudahKeluar.length - index}. 
                <strong>${lagu.judul}</strong>
                - ${lagu.penyanyi}`;


            historyList.appendChild(div);

        });

}


// ================================
// RESET
// ================================

function resetUndian() {

    const konfirmasi =
        confirm(
            "Apakah Anda yakin ingin mereset semua hasil undian?"
        );


    if (!konfirmasi) {
        return;
    }


    laguTersedia = [...daftarLagu];

    laguSudahKeluar = [];


    document.getElementById("status").innerText =
        "SIAP MENGUNDI";


    document.getElementById("judul").innerText =
        "---";


    document.getElementById("penyanyi").innerText =
        "---";


    const video =
        document.getElementById("videoPlayer");


    video.pause();

    video.removeAttribute("src");

    video.load();


    updateHistory();

}


// ================================
// KEYBOARD
// ================================

document.addEventListener("keydown", function(event) {

    if (event.code === "Space") {

        event.preventDefault();

        const button =
            document.getElementById("drawButton");


        if (!button.disabled) {

            undianLagu();

        }

    }

});


// ================================
// START
// ================================

loadSongs();