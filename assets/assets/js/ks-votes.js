function voteArticle(articleId,vote){
        $.get('/votes/set-article-vote',{
            article_id: articleId,
            vote: vote
        }).then(res => {
            if(res === 'no_need_to_change'){

            }else if(res === 'exist_but_invalid'){

            }else if(res === 'not_exist_and_invalid'){

            }else{
                $('#articleVoteArea').html(res);
            }
        })

}

function voteWeek(weekId,vote){
        $.get('/votes/set-week-vote',{
            week_id: weekId,
            vote: vote
        }).then(res => {
            if(res === 'no_need_to_change'){

            }else if(res === 'exist_but_invalid'){

            }else if(res === 'not_exist_and_invalid'){

            }else{
                $('#weekVoteArea').html(res);
            }
        })

}

function voteCCDetail(ccdetailId,vote){
        $.get('/votes/set-ccdetail-vote',{
            ccdetail_id: ccdetailId,
            vote: vote
        }).then(res => {
            if(res === 'no_need_to_change'){

            }else if(res === 'exist_but_invalid'){

            }else if(res === 'not_exist_and_invalid'){

            }else{
                $('#ccdetailVoteArea').html(res);
            }
        })

}

function voteCourse(courseId,vote){
        $.get('/votes/set-course-vote',{
            course_id: courseId,
            vote: vote
        }).then(res => {
            if(res === 'no_need_to_change'){

            }else if(res === 'exist_but_invalid'){

            }else if(res === 'not_exist_and_invalid'){

            }else{
                $('#courseVoteArea').html(res);
            }
        })

}

function voteAudio(audioId,vote){
        $.get('/votes/set-audio-vote',{
            audio_id: audioId,
            vote: vote
        }).then(res => {
            if(res === 'no_need_to_change'){

            }else if(res === 'exist_but_invalid'){

            }else if(res === 'not_exist_and_invalid'){

            }else{
                $('#audioVoteArea'+audioId).html(res);
            }
        })
}
function voteAudioCourse(audioId,vote){
        $.get('/votes/set-audio-course-vote',{
            audio_id: audioId,
            vote: vote
        }).then(res => {
            if(res === 'no_need_to_change'){

            }else if(res === 'exist_but_invalid'){

            }else if(res === 'not_exist_and_invalid'){

            }else{
                $('#audioVoteArea'+audioId).html(res);
            }
        })
}
function voteAudioWeek(audioId,vote){
        $.get('/votes/set-audio-week-vote',{
            audio_id: audioId,
            vote: vote
        }).then(res => {
            if(res === 'no_need_to_change'){

            }else if(res === 'exist_but_invalid'){

            }else if(res === 'not_exist_and_invalid'){

            }else{
                $('#audioVoteArea'+audioId).html(res);
            }
        })
}

function voteAudioArticle(audioId,vote){
        $.get('/votes/set-audio-article-vote',{
            audio_id: audioId,
            vote: vote
        }).then(res => {
            if(res === 'no_need_to_change'){

            }else if(res === 'exist_but_invalid'){

            }else if(res === 'not_exist_and_invalid'){

            }else{
                $('#audioVoteArea'+audioId).html(res);
            }
        })
}

function addToPlaylist(audioId){
    $.get('/votes/add-audio-to-playlist',{
            audio_id: audioId,
        }).then(res => {
            if(res === 'no_need_to_change'){

            }else if(res === 'exist_but_invalid'){

            }else if(res === 'not_exist_and_invalid'){

            }else{
                $('#addToPlaylist'+audioId).html(res);
                // Swal.fire({
                //     icon: 'info',
                //     text: 'این فایل صوتی به لیست پخش شما اضافه شد.',
                //     showConfirmButton: true,
                //
                // })
            }
        })
}
function addToWeekPlaylist(audioId){
    $.get('/votes/add-week-audio-to-playlist',{
            audio_id: audioId,
        }).then(res => {
            if(res === 'no_need_to_change'){

            }else if(res === 'exist_but_invalid'){

            }else if(res === 'not_exist_and_invalid'){

            }else{
                $('#addToPlaylist'+audioId).html(res);
                // Swal.fire({
                //     icon: 'info',
                //     text: 'این فایل صوتی به لیست پخش شما اضافه شد.',
                //     showConfirmButton: true,
                //
                // })
            }
        })
}