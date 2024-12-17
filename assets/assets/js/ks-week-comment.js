$("button").on("click", function (event) {
    event.preventDefault();
    $("<div>")
        .append("default " + event.type + " prevented")
        .appendTo("#log");

});

function sendArticleComment(weekId) {
    var comment = $('#commentText').val();
    var parentId = $('#parent_id').val();
    console.log(parentId);
    if (comment !== "" && comment !== '') {
        $.get('/add-week-comment', {
            week_comment: comment,
            week_id: weekId,
            parent_id: parentId
        }).then(res => {
            $('#commentText').val('');
            $('#parent_id').val('');
            if (res === "no-staff") {
                $('#submitCommentArea').html('<div class="alert alert-info col-lg-12 col-md-12 col-sm-12">نظر شما ثبت شد و بعد از تایید ناظر سایت منتشر خواهد شد.</div>');
                document.getElementById('submitCommentArea').scrollIntoView({behavior: "smooth"});
            } else if(res === 'too-many-comment') {
                Swal.fire({
                    icon: 'error',
                    text: 'تعداد کامنت های ارسالی در 15 دقیقه اخیر برای شما بیش از 3 عدد بوده است. لطفا دقایقی دیگر مجددا تلاش کنید.',
                    showConfirmButton: true,
                })
            } else {
                $('#comments_area').html(res);
                if (parentId !== null && parentId !== '') {
                    document.getElementById('single_comment_box_' + parentId).scrollIntoView({behavior: "smooth"});
                } else {
                    document.getElementById('comments_area').scrollIntoView({behavior: "smooth"});
                }
            }


        });
    }
}

function fillParentId(parentId) {
    $('#parent_id').val(parentId);
    document.getElementById('comment_form').scrollIntoView({behavior: "smooth"});
}


function showMoreDescription(description){
    $('#description_p').text(description);
}