console.log("working fine");

const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

$("#commentForm").submit(function(event) { 
    event.preventDefault();

    let dt = new Date();
    let date = dt.getDate() + " " + monthNames[dt.getUTCMonth()] + ", " + dt.getFullYear();

    $.ajax({
        data : $(this).serialize(),
        method : $(this).attr('method'),
        url : $(this).attr('action'),
        datatype : 'json',
        success : function(response) {
            console.log(response);

            if(response.bool == true) {
                $("#review-res").html("Review Added Successfully!");
                $(".hide-comment-form").hide();
                $(".add-review").hide();


                let _html = '<div class="single-comment justify-content-between d-flex mb-30">'
                    _html += '<div class="user justify-content-between d-flex">'
                    _html += '<div class="thumb text-center">'
                    _html += '<img src="../static/assets/imgs/blog/dummy-image.jpg" alt="" />'
                    _html += '<a href="#" class="font-heading text-brand">' + response.context.user + '</a>'
                    _html += '</div>'
                    
                    _html += '<div class="desc">'
                    _html += '<div class="d-flex justify-content-between mb-10">'
                    _html += '<div class="d-flex align-items-center">'
                    _html += '<span class="font-xs text-muted">' + date + '</span>'
                    _html += '</div>'
                    
                    for(let i = 1; i <= response.context.rating; i++) {
                        
                        _html += '<i class="fa fa-star text-warning"></i>'
                        
                    }

                    _html +=  '</div>'
                    _html +=   '<p class="mb-10">' + response.context.review + '</p>'

                    _html +=  '</div>'
                    _html +=  '</div>'
                    _html += '</div>';

                    $(".comment-list").prepend(_html);
            } else {
                console.log("Response bool is false");
            }
        },
        error: function(xhr, status, error) {
            console.log("AJAX error: " + status + " - " + error);
        }
    });
});


$(document).ready(function () {
    $(".loader").hide();
  
    // Filter checkbox logic
    $(".filter-checkbox, #price-filter-btn").on("click", function () {
        console.log("Filter checkbox clicked");
  
        let filter_object = {};
  
        let min_price = $("#max_price").attr("min") // Default to 0 if min is not set
        let max_price = $("#max_price").val() // Default to Infinity if max is not set

        filter_object.min_price = min_price;
        filter_object.max_price = max_price;

        $(".filter-checkbox").each(function () {
            let filter_key = $(this).data("filter");
  
            filter_object[filter_key] = $("input[data-filter=" + filter_key + "]:checked")
                .map(function () {
                    return this.value;
                })
                .get(); // Ensures an array format
        });
  
        console.log("Sending Filter Data:", filter_object);
  
        $.ajax({
          url: "/filter-products",
          data: filter_object,
          dataType: "json",
          cache: false,  // Prevents caching
          beforeSend: function () {
              console.log("Sending Data...");
          },
          success: function (response) {
              console.log("Data Received");
              $("#filtered-products").html(response.data);
          }
        });
    });
  
    // Log max price when the "Filter by price" button is clicked
    // $(".custome-checkbox button").on("click", function () {
    //     let min_price = parseFloat($("#max_price").attr("min")) || 0; // Default to 0 if min is not set
    //     let max_price = parseFloat($("#max_price").attr("max")) || Infinity; // Default to Infinity if max is not set
    //     let current_price = parseFloat($("#max_price").val()) || 0; // Default to 0 if value is not a number
  
    //     if (isNaN(current_price)) {
    //         console.error("Current Price is not a valid number.");
    //         return;
    //     }
  
    //     console.log("Current Price is:", current_price);
    //     console.log("Max Price is:", max_price);
    //     console.log("Min Price is:", min_price);
  
    //     // Additional validation if needed
    //     if (current_price < min_price || current_price > max_price) {
    //         console.log("Current Price is out of the allowed range.");
    //     }
    // });
  
    // Log max price when the input loses focus (optional)
    $("#max_price").on("blur", function() {
        let min_price = parseFloat($(this).attr("min")) || 0; // Default to 0 if min is not set
        let max_price = parseFloat($(this).attr("max")) || Infinity; // Default to Infinity if max is not set
        let current_price = parseFloat($(this).val()) || 0; // Default to 0 if value is not a number
  
        if (isNaN(current_price)) {
            console.error("Current Price is not a valid number.");
            return;
        }
  
        console.log("Current Price is:", current_price);
        console.log("Max Price is:", max_price);
        console.log("Min Price is:", min_price);
  
        // Additional validation if needed
        if (current_price < min_price || current_price > max_price) {
            console.log("Current Price is out of the allowed range.");
            min_price = Math.round(min_price*100) / 100;
            max_price = Math.round(max_price*100) / 100;

            // console.log("Min Price is:", min_price);
            // console.log("Max Price is:", max_price);
            alert("Please enter a price between " + min_price + " and " + max_price);
            $this.val(min_price);

            $("range").val(min_price);
            $this.focus();

            return false;

        }
    });
  });





// Add to cart functionality

// Add to cart functionality
$(".add-to-cart-btn").on("click", function(response) {

    let this_val = $(this)
    let index = this_val.attr("data-index")

    let quantity = $(".product-quantity-" + index).val()
    let product_title = $(".product-title-" + index).val()

    let product_id = $(".product-id-" + index).val()
    let product_price = $(".current-product-price-" + index).text()

    let product_pid = $(".product-pid-" + index).val()
    let product_image = $(".product-image-" + index).val()

    console.log("Quantity:", quantity);
    console.log("Title:", product_title);

    console.log("Price:", product_price);
    console.log("ID:", product_id);

    console.log("PID:", product_pid);
    console.log("Image:", product_image);

    console.log("Index:", index);
    console.log("Currrent Element:", this_val);

    // Ajax request will go here
    $.ajax({
        url: '/add_to_cart',
        data: {
            'id': product_id,
            'pid': product_pid,
            'product_image': product_image,
            'qty': quantity,
            'title': product_title,
            'price': product_price,
            'image': product_image // Assuming you want to send image info
        },
        dataType: 'json',
        success: function(data){
            this_val.html("✔");
            console.log("Added Product to Cart!");
            $(".cart-items-count").text(response.totalCartItems);
        },
        error: function(error){
            console.log("Error: ", error);
        }
    })

});

// $.ajax({
//     type: 'POST',
//     url: '/add_to_cart',
//     data: {
//         productid: product_id,
//         quantity: quantity,
//         csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
//     },
//     success: function(data){
//         alert('Item added to your cart');
//     }
// });





// // Add to cart functionality

// $("#add-to-cart-btn").on("click", function() {
//     let quantity = $("#product-quantity").val();
//     let product_title = $(".product-title").val();
//     let product_id = $(".product-id").val();
//     let product_price = $("#current-product-price").text();
//     let this_val = $(this);

//     console.log("Quantity:", quantity);
//     console.log("Id:", product_id);
//     console.log("Title:", product_title);
//     console.log("Price:", product_price);
//     console.log("This is:", this_val);

//     $.ajax({
//         url: '/add-to-cart',
//         data: {
//             id: product_id,
//             qty: quantity,
//             title: product_title,
//             price: product_price,
//         },
//         dataType: 'json',
//         beforeSend: function() {
//             console.log("Adding Product to Cart...");
//         },
//         success: function(response) {
//             this_val.html("Item added to cart");
//             console.log("Added Product to Cart!");
//             $(".cart-items-count").text(response.totalCartItems);
//         }
//     });
    
// });


