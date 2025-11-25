function vn = norm_v(vobj, vsur)
    %sv1 = retime(v1, v2.Time, 'nearest');
    %Velocity = v2.Velocity / sv1.Velocity;
    %Velocity = Velocity(:,1);
    %vn = timetable(sv1.Time, Velocity);
    tnew = vobj.Time; %+ seconds(30 * vobj.Velocity);
    vobj.Time = tnew;
    vnew = zeros(height(vobj),1);
    for i=1:height(vobj)
        t = vobj.Time(i);
        dt = abs(t - vsur.Time);
        [~,idx] = min(dt);
        v_nearest = vsur.Velocity(idx);
        vnew(i) = v_nearest;
    end

    vn = vobj.Velocity./vnew;
end