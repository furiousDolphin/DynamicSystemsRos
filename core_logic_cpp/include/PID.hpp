
#ifndef PID_HPP_
#define PID_HPP_

#include <Eigen/Dense>

#include "ValueManager.hpp"


/*
PID musi moc pobierac sygnal z node'a SetpointProvider oraz z System
dodatkowo musi moc pobierac sygnal ze swoich sliderow do sterowania nastawami
*/

class PID
{
    public:
        PID(/*tutaj albo w update musi byc cos w stylu Signal ()*/);
        double do_step(double cur_e);
        void update_params(/*tutaj albo w PID() musi byc cos w stylu Signal ()*/);
        void update_Tp();

    private:
        struct Params
        {
            double Kf;
            double Tf;
            double Kp;
            double Ki;
            double Kd; 

            void update();
            auto as_doubles() const;
        } params_;

        double P_;
        double I_;
        double D_;
        double prev_e_;

        double Tp_;
        double A_;
        double B_;
        

};

//     template <std::size_t I>
//     double get() const 
//     {
//         if constexpr (I == 0)      { return Kf.get_val(); }
//         else if constexpr (I == 1) { return Tf.get_val(); }
//         else if constexpr (I == 2) { return Kp.get_val(); }
//         else if constexpr (I == 3) { return Ki.get_val(); }
//         else if constexpr (I == 4) { return Kd.get_val(); }
//     }
// } params_;

// namespace std 
// {
//     template <>
//     struct tuple_size<PID::Params> : std::integral_constant<std::size_t, 5> {};

//     template <std::size_t I>
//     struct tuple_element<I, Params> 
//     { using type = double; };
// }

#endif
