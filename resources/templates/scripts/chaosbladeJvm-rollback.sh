kubectl exec {{ pod }} -n {{ namespace }} -- 'bash' '-c' \
'/opt/chaosblade/blade destroy {{ experiment_uid }}' \
'/opt/chaosblade/blade revoke {{ agent_uid }}'