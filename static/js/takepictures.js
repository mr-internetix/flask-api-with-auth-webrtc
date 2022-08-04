
document.addEventListener('DOMContentLoaded', () => {

    const startButton = document.querySelector('button#start');
    const captureButton = document.querySelector('button#capture')
    const imagesDiv = document.querySelector('#images');
    const videoElem = document.querySelector('video');
    const canvas = document.querySelector('.photo');
    const ctx = canvas.getContext('2d');
    const stopBtn = document.querySelector('#stop')
    let stream

    startButton.addEventListener('click', async () => {

        startButton.disabled = true;

        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoElem.srcObject = stream;
        videoElem.play()

    })


    function GetFramesOnCanvas() {
        const width = videoElem.videoWidth;
        const height = videoElem.videoHeight;
        canvas.width = width;
        canvas.height = height;

        return setInterval(() => {
            ctx.drawImage(videoElem, 0, 0, width, height)
        }, 16)


    }

    function takePhoto() {
        const imageData = canvas.toDataURL('image/jpg');
        const link = document.createElement('a');
        console.log(imageData)
        sendCapturedImage(imageData)

        link.href = imageData;
        link.setAttribute('download','image')
        link.innerHTML = `<img src="${imageData}" alt="captured-image"/>`;
        imagesDiv.insertAdjacentElement("afterBegin",link)
    }

    function sendCapturedImage(data) {
        const file = DataURIToBlob(data)
        let formdata = new FormData();
        const randomString = () => Math.random().toString(36) + Date.now().toString(36)
        formdata.append('capture_img',file,`image${randomString()}.jpg`)

        fetch('/capture', {
            method: "POST",
            body: formdata

        }).then(response => response.json()).then(result => console.log(result)).catch(err => console.log(err))

        function DataURIToBlob(dataURI) {
            const splitDataURI = dataURI.split(',')
            const byteString = splitDataURI[0].indexOf('base64') >= 0 ? atob(splitDataURI[1]) : decodeURI(splitDataURI[1])
            const mimeString = splitDataURI[0].split(':')[1].split(';')[0]
          
            const ia = new Uint8Array(byteString.length)
            for (let i = 0; i < byteString.length; i++)
              ia[i] = byteString.charCodeAt(i)
          
            return new Blob([ia], { type: mimeString })
          }

    }
    captureButton.addEventListener('click', takePhoto)

    stopBtn.addEventListener('click',()=>{

        clearInterval(GetFramesOnCanvas);   
        // close the camera
        stream.getTracks().forEach((track) => track.stop());
        startButton.disabled = false;
    });
    videoElem.addEventListener('canplay', GetFramesOnCanvas);





})