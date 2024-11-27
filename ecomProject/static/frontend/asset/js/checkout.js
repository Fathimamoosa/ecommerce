$(document).ready(function () {
    $('.paywithRazorpay').click(function (e) {
        e.preventDefault();

        var fname = $("[name='fname']").val();
        var lname = $("[name='lname']").val();
        var email = $("[name='email']").val();
        var phone = $("[name='phone']").val();
        var address = $("[name='address']").val();
        var city = $("[name='city']").val();
        var state = $("[name='state']").val();
        var country = $("[name='country']").val();
        var pincode = $("[name='pincode']").val();

        if (
            fname == "" || lname == "" || email == "" || phone == "" ||
            address == "" || city == "" || state == "" || country == "" || pincode == ""
        ) {
            alert("All fields are mandatory");
            return false;
        } else {
            $.ajax({
                method: "GET",
                url: "/proceed-to-pay",
                success: function (response) {
                    var options = {
                        "key": "rzp_test_dvtXlG4wEE3EVQ", // Enter the Key ID generated from the Dashboard
                        "amount": response.total_price * 100, // Amount should come from the server
                        "currency": "INR",
                        "name": "Acme Corp",
                        "description": "Test Transaction",
                        "image": "https://example.com/your_logo",
                        // "order_id": response.order_id, // Pass the order_id dynamically
                        "handler": function (response) {
                            alert("Payment ID: " + response.razorpay_payment_id);
                            // alert("Order ID: " + response.razorpay_order_id);
                            // alert("Signature: " + response.razorpay_signature);

                            // Send payment response to server for verification
                            $.ajax({
                                method: "POST",
                                url: "/verify-payment",
                                data: {
                                    payment_id: response.razorpay_payment_id,
                                    order_id: response.razorpay_order_id,
                                    signature: response.razorpay_signature
                                },
                                success: function (verificationResponse) {
                                    if (verificationResponse.success) {
                                        alert("Payment Successful");
                                    } else {
                                        alert("Payment Verification Failed");
                                    }
                                }
                            });
                        },
                        "prefill": {
                            "name": fname + " " + lname,
                            "email": email,
                            "contact": phone
                        },
                        "notes": {
                            "address": address
                        },
                        "theme": {
                            "color": "#3399cc"
                        }
                    };
                    var rzp1 = new Razorpay(options);
                    rzp1.on('payment.failed', function (response) {
                        alert("Payment Failed");
                        alert(response.error.code);
                        alert(response.error.description);
                        alert(response.error.source);
                        alert(response.error.step);
                        alert(response.error.reason);
                        alert(response.error.metadata.order_id);
                        alert(response.error.metadata.payment_id);
                    });
                    rzp1.open();
                },
                error: function (error) {
                    alert("Error in initiating payment: " + error.responseJSON.message);
                }
            });
        }
    });
});
