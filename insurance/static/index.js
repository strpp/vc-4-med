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
            alert.error('Error while loading files from database', errorThrown);
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
            alert.error('Error while loading files from database', errorThrown);
        }
    })
)

$('#emitRefund').click(function(){
    $.ajax({
        type: "POST",
        url:  `${insuranceEndpoint}api/emit/refund`,
        contentType: "application/json",
        data: JSON.stringify({'order_ids' : getOrderIdFromCheckbox()}),
        success: function(response){
            if(response.errors.length > 0 ) {
                console.log(response.errors)
                alert(response.errors[0].error)
            }

            if(response.refunds.length > 0){
                console.log(response.refunds)
                let txt = ''
                for(i=0; i<response.refunds.length;i++){
                    txt += `${response.refunds[i].id} successfully refunded with txh ${response.refunds[i].txh}`
                }
                alert(txt)
            }
            location.reload();
        },
        error: function(jqXHR, textStatus, errorThrown) {
            alert('Error while asking for a refund')
            console.log(errorThrown);
        }
    });

})

function loadRefundToEmit(items){
    for(i=0; i<items.length; i++){
        $(`#ordersToBeRefunded`).append(
            `<tr>
                <td>${items[i]._id}</td>
                <td>${items[i].refund_amount}</td>
                <td>${items[i].pharmacy}</td>
                <td>
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
                <td>${items[i]._id}</td>
                <td>${items[i].refund_amount}</td>
                <td>${items[i].pharmacy}</td>
                <td>${items[i].emission_date}</td>
            </tr>`
        )
    }
}

function getOrderIdFromCheckbox(){
    const checkboxes = $('#ordersToBeRefunded').find("input[type='checkbox']:checked")
    
    if(checkboxes.length < 1){
        alert('You must selected at least an item')
        return
    }

    let orderIds = []
    for(i=0; i<checkboxes.length;i++){
        orderIds.push(checkboxes[i].id)
    }

    return orderIds
}