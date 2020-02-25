$(document).ready(function() {
  $('#set_on').click(function() {
    $.post('/rtde2ros/1');
  });
  $('#set_off').click(function() {
    $.post('/rtde2ros/0');
  });
  $('#set_pause').click(function() {
    $.post('/rtde2ros/2');
  });
});

