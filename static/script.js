async function downloadFile(type) {

    const url = document.getElementById("youtube-url").value.trim();
    const loading = document.getElementById("loading");
    const message = document.getElementById("message");

    message.innerHTML = "";

    if (!url) {
        message.innerHTML = '<p style="color:red;">Introduce un enlace válido.</p>';
        return;
    }

    loading.classList.remove("hidden");

    try {

        const response = await fetch("/download", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                url: url,
                type: type
            })
        });

        loading.classList.add("hidden");

        if (!response.ok) {
            const errorData = await response.json();
            message.innerHTML = `<p style="color:red;">${errorData.error}</p>`;
            return;
        }

        const blob = await response.blob();

        const contentDisposition = response.headers.get("Content-Disposition");

        let filename = "download";

        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?([^\"]+)"?/);
            if (match && match[1]) {
                filename = match[1];
            }
        }

        const downloadUrl = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = filename;

        document.body.appendChild(a);
        a.click();

        a.remove();

        window.URL.revokeObjectURL(downloadUrl);

        message.innerHTML = '<p style="color:lime;">Descarga completada.</p>';

    } catch (error) {

        loading.classList.add("hidden");
        message.innerHTML = '<p style="color:red;">Ha ocurrido un error.</p>';
    }
}

function clearInput() {
    document.getElementById("youtube-url").value = "";
    document.getElementById("message").innerHTML = "";
}
