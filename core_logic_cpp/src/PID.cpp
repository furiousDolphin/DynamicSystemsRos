
#include <tuple>
#include "PID.hpp"

PID::PID(double out_min, double out_max) :
    params_{0.0, 0.0, 0.0, 0.0, 0.0, true},
    P_{0.0}, I_{0.0}, D_{0.0},
    A_{0.0}, B_{0.0},
    prev_e_{0.0}, D_prev_{0.0},
    out_min_{out_min}, out_max_{out_max}
{

}

void PID::reset()
{
    P_ = 0.0;
    I_ = 0.0;
    D_ = 0.0;
    prev_e_ = 0.0;
    prev_D_ = 0.0;
}

void PID::set_limits(double out_min, double out_max)
{
    out_min_ = out_min;
    out_max_ = out_max;
}

double PID::do_step(double cur_e)
{
    if (params_.check_and_reset_dirty() || Tp_.check_and_reset_dirty())
    {
        double denominator = 2.0*params_.Tf + Tp_.get_val();
        A_ = (2.0*params_.Kf*params_.Kd)    / denominator;
        B_ = (2.0*params_.Tf-Tp_.get_val()) / denominator; 
    }

    P_ = params_.Kp*cur_e;
    D_ = A_*(cur_e - prev_e_) + B_*prev_D_;
    prev_D_ = D_;


    double pre_output = P_ + I_ + D_;

    bool is_saturated_high = (pre_output >= out_max_ && cur_e > 0);
    bool is_saturated_low  = (pre_output <= out_min_ && cur_e < 0);

    if (!is_saturated_high && !is_saturated_low)
    { I_ = I_ + params_.Ki * (Tp_.get_val() / 2.0) * (cur_e + prev_e_); }

    double final_output = P_ + I_ + D_;

    return std::clamp(final_output, out_min_, out_max_)
}

void PID::update_params(double Kf, double Tf, double Kp, double Ki, double Kd)
{ 
    params_.Kf = Kf;
    params_.Tf = Tf;
    params_.Kp = Kp;
    params_.Ki = Ki;
    params_.Kd = Kd;

    params_.dirty = true;
}

void PID::update_Tp(double Tp)
{ Tp_.set_val(Tp); }

bool PID::Params::check_and_reset_dirty()
{ 
    bool res = dirty;
    dirty = false;
    return res; 
}


