
// $("button").click(function() {
//     alert(this.id); // or alert($(this).attr('id'));
// });

// $(document).ready(function(){
//   $("#img1").click(function(){
//       // Change src attribute of image
//       $(this).attr("src", "img/tm_backtest_cht_10SG_largeCaps20210314W14.png");
//   });    
// });

jQuery(document).ready(function($){

  $('#SG').on({
      'click': function(){
        $('#img1').attr('src','img/tm_backtest_cht_10SG_largeCaps20210314W14.png');
        $('#img2').attr('src','img/tm_mergeImg10SG_largeCaps20210314W1.jpg');
        $('#img3').attr('src','img/tm_mergeImg10SG_largeCaps20210314W4.jpg');
        $('#country').text('Singapore');
        $('#country').css('color','blue');
       }
   });
   
  $('#HKC').on({
      'click': function(){
      $('#img1').attr('src','img/tm_backtest_cht_10HK+ChinaADR20210314W14.png');
      $('#img2').attr('src','img/tm_mergeImg10HK+ChinaADR20210314W1.jpg');
      $('#img3').attr('src','img/tm_mergeImg10HK+ChinaADR20210314W4.jpg');
      $('#country').text('Hong Kong + China ADR');
      $('#country').css('color','darkorange');
      }
   });
      
  $('#US').on({
    'click': function(){
      $('#img1').attr('src','img/tm_backtest_cht_10SPX+NQ20210314W14.png');
      $('#img2').attr('src','img/tm_mergeImg10SPX+NQ20210314W1.jpg');
      $('#img3').attr('src','img/tm_mergeImg10SPX+NQ20210314W4.jpg');
      $('#country').text('US S&P500 + Nasdaq100');
      $('#country').css('color','green');
      }
    });

  $('#Europe').on({
       'click': function(){
        $('#img1').attr('src','img/tm_backtest_cht_10Europe60020210314W14.png');
        $('#img2').attr('src','img/tm_mergeImg10Europe60020210314W1.jpg');
        $('#img3').attr('src','img/tm_mergeImg10Europe60020210314W4.jpg');
        $('#country').text('Europe STOXX600');
        $('#country').css('color','black');
      }
   });
  $('#ADR').on({
    'click': function(){
      $('#img1').attr('src','img/tm_backtest_cht_10ADRs_Top30020210314W14.png');
      $('#img2').attr('src','img/tm_mergeImg10ADRs_Top30020210314W1.jpg');
      $('#img3').attr('src','img/tm_mergeImg10ADRs_Top30020210314W4.jpg');
      $('#country').text('US ADR');
      $('#country').css('color','red');
    }
    });
  });



