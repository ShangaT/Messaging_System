function Random_String()
{
  var str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
  var result = "";
  var max = str.length - 1, min = 0;

  for (let i=0; i<32; i++)
  {
    result += str[Math.floor(Math.random() * max - min + 1) + min];
  }
  document.getElementById("password1").value = document.getElementById("password2").value = result;
  document.getElementById("result").value = "Не забудьте сохранить полученный пароль в надежном месте";
}
