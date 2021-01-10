const uploadForm = document.getElementById('upload-form')
const input = document.getElementById('id_file_name')
const alertBox = document.getElementById('alert-box')
const imageBox = document.getElementById('image-box')
const progressBox = document.getElementById('progress-box')
const cancelBox = document.getElementById('cancel-box')
const cancelBtn = document.getElementById('cancel-btn')
const csrf = document.getElementsByName('csrfmiddlewaretoken')


input.addEventListener('change', ()=>{
    progressBox.classList.remove('invisible')
    cancelBox.classList.remove('invisible')

    const img_data = input.files[0]
    const url = URL.createObjectURL(img_data)
    const fd = new FormData()
    fd.append('csrfmiddlewaretoken', csrf[0].value)
    fd.append('file_name', img_data)

    $.ajax({
        type:'POST',
        url: uploadForm.action,
        enctype:'multipart/form-data',
        data: fd,
        beforeSend: function(){    
            alertBox.innerHTML=""        
            imageBox.innerHTML=""        
        },
        xhr: function(){
            const xhr = new window.XMLHttpRequest();
            xhr.addEventListener('progress', e=>{
                if (e.lengthComputable) {
                    const percent = (e.loaded/e.total)*100
                    progressBox.innerHTML = `<div class="progress">
                                                <div class="progress-bar" role="progressbar" style="width: ${percent}%;" aria-valuenow="${percent}" aria-valuemin="0" aria-valuemax="100">${percent}%</div>
                                            </div>`
                }
            })
            cancelBtn.addEventListener('click', ()=>{
                xhr.abort()
                setTimeout(()=>{
                    uploadForm.reset()
                    progressBox.innerHTML = ""
                    alertBox.innerHTML = ""
                    cancelBox.classList.add('invisible')
                }, 2000)                
            })
            return xhr

        },
        success: function(response){
            imageBox.innerHTML = `<img src="/static/img/upload-csv-icon.png" width="100px">`
            alertBox.innerHTML = `<div class="alert alert-success" role="alert">
                                    Sucesso ao carregar o arquivo !!!
                                </div>`
            cancelBox.classList.add('invisible')
        },
        error: function(error){
            alertBox.innerHTML = `<div class="alert alert-danger" role="alert">
                                    Erro ao carregar o arquivo !!!
                                </div>`
        },
        cache: false,
        contentType: false,
        processData: false,
    })

})

