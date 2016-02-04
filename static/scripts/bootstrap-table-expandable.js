(function ($) {
    $(function () {
        $('.table-expandable').each(function () {
            var table = $(this);
            table.children('thead').children('tr').prepend('<th class="arrow-cell"></th>');
            table.children('tbody').children('tr').hide();
            table.children('tbody').children('tr').filter('.top-level').show();
            table.children('tbody').children('tr').filter('.expandable').click(function () {
                var element = $(this);
                element.next('tr').toggle('fast');
                element.find(".table-expandable-arrow").toggleClass("up");
            });
            table.children('tbody').children('tr').filter('.expandable').each(function () {
                var element = $(this).children('.arrow-cell');
                element.prepend('<div class="table-expandable-arrow"></div>');
            });
        });
    });
})(jQuery); 