/etc/conjur.pem:
  file:
    - managed
    - mode: 600
    - contents_pillar: conjur:certificate