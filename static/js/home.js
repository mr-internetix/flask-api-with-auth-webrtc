document.addEventListener('DOMContentLoaded',()=>{
const submitBtn = document.getElementById('submitBtn');
const fileInput = document.getElementById('fileInput');


submitBtn.addEventListener('click',(e)=>{
    e.preventDefault; 
    const file = fileInput.files[0];
    console.log(file)
    let formdata = new FormData();
    formdata.append('my_file',file)

    fetch('/upload',{
        method:"POST",
        body:formdata
    }).then(response => response.json()).then(result =>
         window.location.href = result.url).catch(err=> alert(err))

    

})



})