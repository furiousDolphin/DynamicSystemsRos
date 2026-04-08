
#include <tuple>
#include "PID.hpp"

PID::PID(/*tutaj albo w update musi byc cos w stylu Signal ()*/)
{

}

double PID::do_step(double cur_e)
{
    double Tp;     //trzeba pobrac

    auto [Kf, Tf, Kp, Ki, Kd] = params_;

    P_ = Kp*cur_e;
    I_ = I_ + Ki*(Tp/2)*(cur_e + prev_e);
}

void PID::update(/*tutaj albo w PID() musi byc cos w stylu Signal ()*/)
{
    //Tp = ...;
    A_ = (2*Kf*Kd)/(2*Tf+Tp)
    B_ = (2*Tf-Tp)/()
}

auto PID::Params::as_doubles() const
{ return std::tuple(Kf.get_val(), Tf.get_val(), Kp.get_val(), Ki.get_val(), Kd.get_val()) }

void PID::Params::update(/*tutaj albo w PID() musi byc cos w stylu Signal ()*/)
{
    
}

bool PID::Params::check_dirty() const
{ eturn (Kf.check_dirty() || Tf.check_dirty() || Kp.check_dirty() || Ki.check_dirty() || Kd.check_dirty()) }
