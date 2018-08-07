<script type="text/javascript">
$(document).ready(function() {
    $('#selecctall_1').click(function(event) {
        if (this.checked) {
            $('.jqselect_1').each(function() { //loop through each checkbox
                $(this).prop('checked', true); //check
            });
        } else {
            $('.jqselect_1').each(function() { //loop through each checkbox
                $(this).prop('checked', false); //uncheck
            });
        }
    });
    $('#selecctall_2').click(function(event) {
        if (this.checked) {
            $('.jqselect_2').each(function() { //loop through each checkbox
                $(this).prop('checked', true); //check
            });
        } else {
            $('.jqselect_2').each(function() { //loop through each checkbox
                $(this).prop('checked', false); //uncheck
            });
        }
    });
    $('#selecctall_3').click(function(event) {
        if (this.checked) {
            $('.jqselect_3').each(function() { //loop through each checkbox
                $(this).prop('checked', true); //check
            });
        } else {
            $('.jqselect_3').each(function() { //loop through each checkbox
                $(this).prop('checked', false); //uncheck
            });
        }
    });
    $('#selecctall_4').click(function(event) {
        if (this.checked) {
            $('.jqselect_4').each(function() { //loop through each checkbox
                $(this).prop('checked', true); //check
            });
        } else {
            $('.jqselect_4').each(function() { //loop through each checkbox
                $(this).prop('checked', false); //uncheck
            });
        }
    });
    $('#selecctall_5').click(function(event) {
        if (this.checked) {
            $('.jqselect_5').each(function() { //loop through each checkbox
                $(this).prop('checked', true); //check
            });
        } else {
            $('.jqselect_5').each(function() { //loop through each checkbox
                $(this).prop('checked', false); //uncheck
            });
        }
    });
});
</script>
