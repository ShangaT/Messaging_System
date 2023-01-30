function Random_String()
{
  var password1 = document.getElementById("password1");
  var password2 = document.getElementById("password2");

  var str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,-_!?*";
  var result = "";
  var max = str.length - 1, min = 0;

  for (let i=0; i<32; i++)
  {
    result += str[Math.floor(Math.random() * max - min + 1) + min];
  }

  password1.type = "password";
  password2.type = "password";

  document.getElementById("password1").value = document.getElementById("password2").value = result;
  document.getElementById("result").value = "Не забудьте сохранить полученный пароль в надежном месте";
}

function Matching_Passwords()
{
  var password1 = document.getElementById("password1").value;
  var password2 = document.getElementById("password2").value;

  if (password1 != password2)
  {
    document.getElementById("result").value = "Пароли должны совпадать";
    return false;
  }
  else
  {
    return true;
  }
}

function Show_Password()
{
  var password1 = document.getElementById("password1");
  var password2 = document.getElementById("password2");
  if (password1.type === "password" && password2.type === "password")
  {
    password1.type = "text";
    password2.type = "text";
  }
  else
  {
    password1.type = "password";
    password2.type = "password";
  }
}

function Show_Error()
{
  document.getElementById("result").value = "Вы зарегестрированы";
}
