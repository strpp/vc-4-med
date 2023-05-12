import { showPopupBox, showPopupMsg } from "./popupBox.js"

const credentialEndpoint = 'http://192.168.1.20:5001/api/credentials'
const insuranceEndpoint = 'http://192.168.1.20:5002/api/refund'

$('#sendCredentials').click(function(){
    $.getJSON(credentialEndpoint, function(data){
        sendVpsToInsurance(data)
    })
})

function sendVpsToInsurance(data){
    if(data) {
        $.ajax({
            type: 'POST',
            url: insuranceEndpoint,
            //headers: {'Origin': 'https://192.168.1.20:5001'},
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
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

$('#reset').click(function(){
    vps = null
})        