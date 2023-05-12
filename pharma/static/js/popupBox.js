function showPopupBox(status, txt){

    $('#popupHeader').empty()
    $('#popupText').empty()

    $('.popupBox').addClass(status)
    $('.popupBox').css('visibility', 'visible')

    $('#popupHeader').append(`${status}!`)
    $('#popupText').append(`${txt}`)

    if(status == 'success'){
        $('.popupBox').append(
            `<button onclick="this.parentElement.style.visibility='hidden'; location.reload();">Ok</button>`
        )
    }
}

function showPopupMsg(msgs){

    $('#popupHeader').empty()
    $('#popupText').empty()

    $('.popupBox').addClass('message')
    $('.popupBox').css('visibility', 'visible')

    $('#popupHeader').append(`A new message:`)
    for(let m=0; m <msgs.length; m++){
        if(msgs[m].status == 'error') $('#popupText').append(showError(msgs[m]))
        else if(msgs[m].status == 'success') $('#popupText').append(showSuccess(msgs[m]))

    }
}

function showError(msg){
    msg =`<p>
    Order: ${msg.id} <br> 
    <i class="fa-solid fa-circle-exclamation" style="color: #ff0000;"></i>
    Error: ${msg.error}
    </p>`
    return msg
}

function showSuccess(msg){
    msg =`<p>
    Order ${msg.id}: <br>
    <i class="fa-solid fa-check" style="color: #00ff00;"></i>
    txh ${msg.txh} refunded ${msg.amount}
    </p>`
    return msg
}

export {showPopupBox, showPopupMsg};