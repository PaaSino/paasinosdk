username='' # FILL ME
password='' # FILL ME
address='' # FILL ME
arvan paas create secret docker-registry private-reg \
  --docker-username=${username} \
  --docker-password=${password} \
  --docker-server=${address}

