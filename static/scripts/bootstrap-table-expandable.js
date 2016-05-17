(function ($) {
    $(function () {
        $('.table-expandable').each(function () {
            var table = $(this);
            table.children('thead').children('tr').prepend('<th class="arrow-cell"></th>');
            table.children('tbody').children('tr').hide();
            table.children('tbody').children('tr').filter('.top-level').show();
            table.children('tbody').children('tr').filter('.expandable').click(function () {
                var element = $(this);
                if (element.hasClass('top-level') && element.find(".table-expandable-arrow").hasClass('up')) {
                    topID = '.' + element.attr('id');
                    table.children('tbody').children('tr').filter(topID).find(".table-expandable-arrow").removeClass('up')
                    table.children('tbody').children('tr').filter(topID).hide();
                    element.find(".table-expandable-arrow").toggleClass("up");
                }
                else {
                    element.next('tr').toggle('fast');
                    element.find(".table-expandable-arrow").toggleClass("up");
                }
            });
            table.children('tbody').children('tr').filter('.expandable').each(function () {
                var element = $(this).children('.arrow-cell');
                element.prepend('<div class="table-expandable-arrow"></div>');
            });
        });
    });
})(jQuery);