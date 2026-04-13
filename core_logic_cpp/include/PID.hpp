
#ifndef PID_HPP_
#define PID_HPP_

#include <Eigen/Dense>

#include "ValueManager.hpp"


class PID
{
    public:
        PID();
        double do_step(double cur_e);
        void update_params(double Kf, double Tf, double Kp, double Ki, double Kd);
        void update_Tp(double Tp);
        void reset();
        void set_limits(double out_min, double out_max);

    private:
        struct Params
        {
            double Kf;
            double Tf;
            double Kp;
            double Ki;
            double Kd; 

            bool dirty;

            bool check_and_reset_dirty()
        } params_;

        double P_;
        double I_;
        double D_;

        ValueManager Tp_;
        double A_;
        double B_;

        double prev_e_;
        double prev_D_;
};

#endif
