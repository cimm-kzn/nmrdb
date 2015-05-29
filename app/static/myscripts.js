function myF(nomer)
{
alert("nomer  = "+nomer);
 myname = "g"+nomer;
 myObj=document.getElementById(myname);
 alert(myObj);
if(myObj)
{
 myObj.innerHTML="<img src='galka.jpg' alt='ìåäóçà' height=40 width=40>";
 }
}
