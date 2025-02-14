console.log("working fine");

const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

// Function to attach event listeners to delete buttons
function attachDeleteListeners() {
    $(".delete-product").on("click", function () {
        const product_id = $(this).attr("data-product");
        const this_val = $(this);

        console.log("Product ID:", product_id);

        $.ajax({
            url: "/delete-from-cart",
            data: { "id": product_id },
            dataType: "json",
            beforeSend: () => this_val.hide(),
            success: (response) => {
                console.log("Product deleted successfully:", response);
                $(".cart-items-count").text(response.totalCartItems);
                $("#cart-list").html(response.data);
                attachUpdateListeners();
                attachDeleteListeners(); // Re-attach listeners
                this_val.show();
            },
            error: (xhr, status, error) => {
                console.log("AJAX error: " + status + " - " + error);
                this_val.show();
            },
        });
    });
}

// Function to attach event listeners to update buttons
function attachUpdateListeners() {
    $(".update-product").on("click", function () {
        const product_id = $(this).attr("data-product");
        const sanitized_product_id = product_id.replace(/\//g, "");
        const this_val = $(this);
        const product_quantity = $(`.product-qty-${sanitized_product_id}`).val();

        console.log("Product ID:", product_id);
        console.log("Sanitized Product ID:", sanitized_product_id);
        console.log("Quantity:", product_quantity);

        if (product_quantity <= 0) {
            alert("Quantity must be greater than 0.");
            return;
        }

        $.ajax({
            url: "/update-cart",
            method: "GET",
            data: { "id": product_id, "qty": product_quantity },
            dataType: "json",
            beforeSend: () => this_val.hide(),
            success: (response) => {
                console.log("Cart updated successfully:", response);
                $(".cart-items-count").text(response.totalcartitems);
                $("#cart-list").html(response.data);
                attachUpdateListeners(); // Re-attach update listeners
                attachDeleteListeners(); // Re-attach delete listeners
                this_val.show();
            },
            error: (xhr, status, error) => {
                console.error("AJAX Error:", status, error);
                alert("An error occurred while updating the cart. Please try again.");
                this_val.show();
            },
        });
    });
}

// Function to handle filter checkbox logic
function attachFilterListeners() {
    $(".filter-checkbox, #price-filter-btn").on("click", function () {
        console.log("Filter checkbox clicked");

        const filter_object = {
            min_price: $("#max_price").attr("min"),
            max_price: $("#max_price").val(),
        };

        $(".filter-checkbox").each(function () {
            const filter_key = $(this).data("filter");
            filter_object[filter_key] = $(`input[data-filter=${filter_key}]:checked`)
                .map(function () {
                    return this.value;
                })
                .get();
        });

        console.log("Sending Filter Data:", filter_object);

        $.ajax({
            url: "/filter-products",
            data: filter_object,
            dataType: "json",
            cache: false,
            beforeSend: () => console.log("Sending Data..."),
            success: (response) => {
                console.log("Data Received");
                $("#filtered-products").html(response.data);
            },
        });
    });
}

// Function to handle price validation on blur
function attachPriceValidation() {
    $("#max_price").on("blur", function () {
        const min_price = parseFloat($(this).attr("min")) || 0;
        const max_price = parseFloat($(this).attr("max")) || Infinity;
        const current_price = parseFloat($(this).val()) || 0;

        if (isNaN(current_price)) {
            console.error("Current Price is not a valid number.");
            return;
        }

        console.log("Current Price is:", current_price);
        console.log("Max Price is:", max_price);
        console.log("Min Price is:", min_price);

        if (current_price < min_price || current_price > max_price) {
            console.log("Current Price is out of the allowed range.");
            alert(`Please enter a price between ${min_price} and ${max_price}`);
            $(this).val(min_price).focus();
            return false;
        }
    });
}

// Function to handle add to cart logic
function attachAddToCartListeners() {
    $(".add-to-cart-btn").on("click", function () {
        const this_val = $(this);
        const index = this_val.attr("data-index");

        const quantity = $(`.product-quantity-${index}`).val();
        const product_title = $(`.product-title-${index}`).val();
        const product_id = $(`.product-id-${index}`).val();
        const product_price = $(`.current-product-price-${index}`).text();
        const product_pid = $(`.product-pid-${index}`).val();
        const product_image = $(`.product-image-${index}`).val();

        console.log("Quantity:", quantity);
        console.log("Title:", product_title);
        console.log("Price:", product_price);
        console.log("ID:", product_id);
        console.log("PID:", product_pid);
        console.log("Image:", product_image);
        console.log("Index:", index);
        console.log("Current Element:", this_val);

        $.ajax({
            url: '/add_to_cart',
            data: {
                'id': product_id,
                'pid': product_pid,
                'product_image': product_image,
                'qty': quantity,
                'title': product_title,
                'price': product_price,
                'image': product_image
            },
            dataType: 'json',
            success: (response) => {
                this_val.html("✔");
                console.log("Added Product to Cart!");
                $(".cart-items-count").text(response.totalCartItems);
            },
            error: (error) => {
                console.log("Error: ", error);
            },
        });
    });
}


// Initialize all event listeners
$(document).ready(function () {
    $(".loader").hide();
    attachDeleteListeners();
    attachUpdateListeners();
    attachFilterListeners();
    attachPriceValidation();
    attachAddToCartListeners();

    $(document).on("click", ".make-default-address", function(){

        let id = $(this).attr("data-address-id");
        let this_val = $(this);
    
        console.log("ID is:", id);
        console.log("Element is:", this_val);
    
        $.ajax({
            url: "/make-default-address",
            data: {
                'id': id  // Corrected: Added 'id' as the key and the id variable as the value
            },
            dataType: "json",
            success: function(response){
                console.log("Address Made Default....");

                if (response.boolean == true) { // or if (response.boolean) is sufficient
                    $(".check").hide();
                    $(".action_btn").show();

                    $(".check" + id).show(); // Correct way to concatenate in jQuery selector
                    $(".button" + id).hide(); // Correct way to concatenate in jQuery selector
                }
            }
        });
    });
});




