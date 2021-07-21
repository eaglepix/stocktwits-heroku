
// $("button").click(function() {
//     alert(this.id); // or alert($(this).attr('id'));
// });

// $(document).ready(function(){
//   $("#img1").click(function(){
//       // Change src attribute of image
//       $(this).attr("src", "img/tm_backtest_cht_10SG_largeCaps20210314W14.png");
//   });    
// });

// $.ajax({
//   url: "test.html",
//   type: "GET", 
//   crossDomain: true,
//   context: document.body
// }).done(function() {
//   $( this ).addClass( "done" );
// });

// jQuery(document).ready(function($){

$('#SG').on({
  'click': function () {
    $('#img1').attr('src', 'https://drive.google.com/uc?id=1K5zVD11NJTy13NTct3ZFvs91nSy5_cgD');
    $('#img2').attr('src', 'https://drive.google.com/uc?id=19uAJ8cQDswD6eizLQQ6redKJqLg1hXz9');
    $('#img3').attr('src', 'https://drive.google.com/uc?id=1hw1EOTQznRE5yE00HWknjD_KcvhiQtkh');
    $('#country').text('Singapore');
    $('#country').css('color', 'blue');
  }
});

$('#HKC').on({
  'click': function () {
    $.ajax('https://drive.google.com/file/d/12Xx0edSdP6hhP32vjgJELusV9UH3-Lor/view?usp=sharing'), {
      success: function (data) {
        $('#img1').attr('src', $(data));
      },
      error: function () {
        console.log(`An error occurred: ${HKC}`)
      }
    };

    $('#img2').attr('src', 'https://drive.google.com/file/d/1WQzsNeIPl_cbj6RqoUfCye4rdcryEedL/view?usp=sharing');
    $('#img3').attr('src', 'https://drive.google.com/file/d/1SFzaAGesIIFBqmIC3Tc29cs2EvQTApX1/view?usp=sharing');
    $('#country').text('Hong Kong + China ADR');
    $('#country').css('color', 'darkorange');
  }
});

$('#US').on({
  'click': function () {
    $('#img1').attr('src', 'img/tm_backtest_cht_10SPX+NQ20210314W14.png');
    $('#img2').attr('src', 'img/tm_mergeImg10SPX+NQ20210314W1.jpg');
    $('#img3').attr('src', 'img/tm_mergeImg10SPX+NQ20210314W4.jpg');
    $('#country').text('US S&P500 + Nasdaq100');
    $('#country').css('color', 'green');
  }
});

$('#Europe').on({
  'click': function () {
    $('#img1').attr('src', 'img/tm_backtest_cht_10Europe60020210314W14.png');
    $('#img2').attr('src', 'img/tm_mergeImg10Europe60020210314W1.jpg');
    $('#img3').attr('src', 'img/tm_mergeImg10Europe60020210314W4.jpg');
    $('#country').text('Europe STOXX600');
    $('#country').css('color', 'black');
  }
});
$('#ADR').on({
  'click': function () {
    $('#img1').attr('src', 'img/tm_backtest_cht_10ADRs_Top30020210314W14.png');
    $('#img2').attr('src', 'img/tm_mergeImg10ADRs_Top30020210314W1.jpg');
    $('#img3').attr('src', 'img/tm_mergeImg10ADRs_Top30020210314W4.jpg');
    $('#country').text('US ADR');
    $('#country').css('color', 'red');
  }
});



