var categories;

$(document).ready(function() {
    $(".member-list .member").click(function() {
       if($(this).hasClass("active")) {
            $(this).removeClass("active");
        } else {
            $(this).parents(".member-list").find(".member").removeClass("active");
            $(this).addClass("active");
        }
    });

    $("[title]").tooltip();

    $("table.list tr.item").click(function() {
        var link = $(this).find("a.item-link").attr("href");
        if(link) {
            window.location = link;
        }
    });

    $(".shopping.list .item td.status").click(function(e) {
        var item = $(this).parents(".item");
        var old_status = item.attr("data-status");
        if(old_status == "editing") return;
        var new_status = item.attr("data-status") == "purchased" ? "reset" : "purchased";
        var id = item.attr("data-id");

        item.attr("data-status", "working");

        $.ajax({
            type: "POST",
            url: "/api/shopping/item/status/" + id + "/" + new_status,
            dataType: "json",
            success: function(data) {
                item.attr("data-status", data.item.purchased ? "purchased" : "unpurchased");
            }
        });
        e.preventDefault();
    });

    $(".shopping.list .item").find("td.title .title,td.title .description,td.amount,td.category").click(function(e) {
        $(this).editStart();
    });

    prepareAutocomplete();
    $('[data-autocomplete="ShoppingCategory"]').autocompleteShoppingCategory();
    $(".autofocus").focus();
});

$.fn.editStart = function() {
    if($(this).hasClass("editing")) return;
    $("*").editStop();
    $(this).each(function() {
        var item = $(this).parents(".item");
        var target = $(this);

        var input = $('<input type="text" class="form-control" />');

        var value = $(this).text();
        input.val(value.trim());

        var form = $('<form method="POST" action="?edit=' + item.attr("data-id") + '"></form>');
        form.append(input);

        $(this).data("current-value", value);
        $(this).html(form).addClass("editing");

        if($(this).hasClass("category")) {
            input.autocompleteShoppingCategory();
        }

        input.focus();

        $(document).keyup(function(e) {
            if(e.keyCode == 27) { 
                target.editStop();
            }
        });
    });
};

$.fn.editStop = function() {
    $(this).each(function() {
        if($(this).hasClass("editing")) {
           $(this).html($(this).data("current-value")).removeClass("editing");
        }
    });
};


function prepareAutocomplete() {
    categories = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('title'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        limit: 10,
        prefetch: {
            ttl: 100,
            url: '/api/shopping/categories',
            filter: function(result) {
                return result.categories;
            }
        }
    });
    
    categories.initialize();
} 

$.fn.autocompleteShoppingCategory = function() {
    $(this).typeahead(null, {
        name: 'categories',
        displayKey: 'title',
        source: categories.ttAdapter(),
        templates: {
            suggestion: Handlebars.compile('<p>{{title}} <span class="pull-right" style="color: lightgray;">{{item_count}} items</span></p>')
        }
    });

}