import { showPopupBox, showPopupMsg } from "./popupBox.js"

const credentialEndpoint = 'http://192.168.1.20:5001/api/credentials'
const insuranceEndpoint = 'http://192.168.1.20:5002/api/refund'

$( document ).ready(

    $.ajax({   
        type: 'GET',
        url: 'http://192.168.1.20:5001/api/receipts' ,
        contentType: 'application/json',
        
        success: function(response) {
            loadTable(response)
        },
        
        error: function(jqXHR, textStatus, errorThrown) {
            showPopupBox('alert', 'Error while loading files from database');
        }
    })
);

$('#sendCredentials').click(function(){
    $.getJSON(credentialEndpoint, function(data){
        if(!data.length) showPopupBox('alert', 'There is no credentials to send')
        else sendVpsToInsurance(data)
    })
})

function updateRefundToPending(refunds){

    $.ajax({
        type: 'POST',
        url: 'http://192.168.1.20:5001/api/credentials/pending',
        contentType: 'application/json',
        data: JSON.stringify({'order_ids' : refunds}),
        success: function(response){ console.log('updated correctly')},
        error: function(jqXHR, textStatus, errorThrown) { console.log('error while uploading')
    }
    });
}

function sendVpsToInsurance(data){
    if(data) {
        $.ajax({
            type: 'POST',
            url: insuranceEndpoint,
            //headers: {'Origin': 'https://192.168.1.20:5001'},
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                console.log(response)
                let msgs = []
                if(response['errors']){
                    for(let i=0; i< response['errors'].length; i++){
                        msgs.push({
                            'id':response['errors'][i].id,
                            'error':response['errors'][i].error,
                            'status':'error'
                        })
                    }
                }

                if(response['refunds']){
                    for(let i=0; i< response['refunds'].length; i++){
                        msgs.push({
                            'id':response['refunds'][i].id,
                            'txh':response['refunds'][i].txh,
                            'amount':response['refunds'][i].amount,
                            'status':'success'
                        })
                    }
                    updateRefundToPending(response['refunds'])
                }
                showPopupMsg(msgs);
            },
            error: function(jqXHR, textStatus, errorThrown) {
            showPopupBox('alert', `Error sending files to Insurance: ${errorThrown} `);
        }
        });
    }
    else showPopupBox('alert', 'error: no vps to send')
}

function loadTable(items){
    console.log(items)
    for(let i=0; i<items.length; i++){
        $(`#credentialsToSend`).append(
            `<tr>
                <td style="width: 350px">
                    ${items[i]._id}
                </td>
                <td style="width: 100px">
                    ${items[i].refunded}
                </td>
                <td style="width: 450px">
                    ${items[i].date}
                </td>
                <td style="width: 312px">
                    <input type="checkbox" id=${items[i]._id} name=${items[i]._id} value=${items[i]._id}>
                </td>
            </tr>`
        )
    }
}

$('#selectAll').click(function(){
    const checkboxes = $('#credentialsToSend').find("input[type='checkbox']")
    for(i=0; i<checkboxes.length;i++){
        checkboxes.prop('checked', true);
    }
})

$('#resetAll').click(function(){
    const checkboxes = $('#credentialsToSend').find("input[type='checkbox']")
    for(i=0; i<checkboxes.length;i++){
        checkboxes.prop('checked', false);
    }
})