const insuranceEndpoint = 'http://192.168.1.20:5002/'

$( document ).ready(

    $.ajax({   
        type: 'GET',
        url: `${insuranceEndpoint}api/refund/false` ,
        contentType: 'application/json',
        
        success: function(response) {
            console.log(response)
            loadRefundToEmit(response)
        },
        
        error: function(jqXHR, textStatus, errorThrown) {
            showPopupBox('alert', 'Error while loading files from database');
        }
    }),

    $.ajax({   
        type: 'GET',
        url: `${insuranceEndpoint}api/refund/true` ,
        contentType: 'application/json',
        
        success: function(response) {
            loadRefundEmitted(response)
        },
        
        error: function(jqXHR, textStatus, errorThrown) {
            showPopupBox('alert', 'Error while loading files from database');
        }
    })
)

$('#emitRefund').click(function(){

    const checkboxes = $('#ordersToBeRefunded').find("input[type='checkbox']:checked")

    if(checkboxes.length < 1){
        showPopupBox('alert', 'You must selected at least an item')
        return
    }

    $.ajax({
        type: "POST",
        url:  `${insuranceEndpoint}api/emit/refund`,
        contentType: "application/json",
        data: JSON.stringify({'order_ids' : getOrderIdFromCheckbox()}),
        success: function(response){
            console.log(response)

            if(response.errors.length > 0 ) {
                console.log(response.errors)
                showPopupBox('alert', response.errors[0].error)
            }

            if(response.refunds.length > 0){
                console.log(response.refunds)
                let txt = ''
                for(i=0; i<response.refunds.length;i++){
                    txt += `${response.refunds[i].id} successfully refunded with txh ${response.refunds[i].txh} \n`
                }
                showPopupBox('success', txt)
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus)
            showPopupBox('alert', 'Error while asking for a refund: check account balance')
            console.log(errorThrown);
        }
    });

})

function loadRefundToEmit(items){
    for(i=0; i<items.length; i++){
        $(`#ordersToBeRefunded`).append(
            `<tr>
                <td style="width: 350px">
                    <a href='http://192.168.1.20:5002/api/order/${items[i]._id}'>
                    ${items[i]._id}
                    </a>    
                </td>
                <td style="width: 100px">${items[i].refund_amount}</td>
                <td style="width: 450px">${items[i].pharmacy}</td>
                <td style="width: 312px">
                    <input type="checkbox" id=${items[i]._id} name=${items[i]._id} value=${items[i]._id}>
                </td>
            </tr>`
        )
    }
}

function loadRefundEmitted(items){
    for(i=0; i<items.length; i++){
        $(`#orderAlreadyRefunded`).append(
            `<tr>
                <td style="width: 350px">
                <a href='http://192.168.1.20:5002/api/order/${items[i]._id}'>
                    ${items[i]._id}
                </a>    
                </td>
                <td style="width: 100px">${items[i].refund_amount}</td>
                <td style="width: 450px">${items[i].pharmacy}</td>
                <td style="width: 350px">${items[i].emission_date}</td>
            </tr>`
        )
    }
}

function getOrderIdFromCheckbox(){
    const checkboxes = $('#ordersToBeRefunded').find("input[type='checkbox']:checked")
    
    let orderIds = []
    for(i=0; i<checkboxes.length;i++){
        orderIds.push(checkboxes[i].id)
    }

    return orderIds
}

function showPopupBox(status, txt){

    $('#popupHeader').empty()
    $('#popupText').empty()

    $('.popupBox').addClass(status)
    $('.popupBox').css('visibility', 'visible')

    $('#popupHeader').append(`${status}!`)
    $('#popupText').append(txt)

    if(status == 'success'){
        $('.popupBox').append(
            `<button onclick="this.parentElement.style.visibility='hidden'; location.reload();">Ok</button>`
        )
    }
}

$('#selectAllRefund').click(function(){
    const checkboxes = $('#ordersToBeRefunded').find("input[type='checkbox']")
    for(i=0; i<checkboxes.length;i++){
        checkboxes.prop('checked', true);
    }
})

$('#resetRefundSelection').click(function(){
    const checkboxes = $('#ordersToBeRefunded').find("input[type='checkbox']")
    for(i=0; i<checkboxes.length;i++){
        checkboxes.prop('checked', false);
    }
})