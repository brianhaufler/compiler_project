program arrayRefTest (input, output);
 var a, b : integer;
     x : array [1..5] of real;
begin
  read(a);
  read(b);
  x[a] := 6.783;
  write(a);
  write(b);
  write(x[a])
end.
