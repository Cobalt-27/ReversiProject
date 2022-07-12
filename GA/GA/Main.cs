using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GA
{
    class Main
    {
        // See https://aka.ms/new-console-template for more information
        static readonly int condCount = 4;
        static readonly int weightCount = 3;
        static Random rand = new Random();
        public class Weight
        {
            public int[] val = new int[] { -100, 20, -20, -5, -1, -1, 0, 2, 1, 0, 2, 1, 0, 2, 1, 5, 0, 0 };
        };
        public class Cond
        {
            public int[] val = new int[] { 0,20,45,55};
        };

        public void Run()
        {
            Cond cond = new();
            List<Weight> wlist = new();
            Dictionary<Weight, int> scores = new();
            int initSize = 20;
            for (int i = 0; i < initSize; i++)
                wlist.Add(RandWeight());

            NewJob(RandWeight(),new Cond(),RandWeight(),new Cond()).Wait();
        }

        Weight Cross(Weight a, Weight b)
        {
            Weight res = new();
            res.val=a.val.Select((item, i) => rand.NextDouble() > 0.5 ? a.val[i] : b.val[i]).ToArray();
            return res;
        }

        Weight RandWeight()
        {
            Weight res = new();
            for (int i = 0; i < condCount; i++)
                for (int j = 0; j < weightCount; j++)
                    res.val[i, j] = rand.Next() % 10;
            return res;
        }


        async Task<int> NewJob(Weight w0,Cond c0,Weight w1,Cond c1)
        {
            return await Task.Run(() =>
            {
                Console.WriteLine("Hello, World!");
                var path = @"C:\Users\Clover\Desktop\AI\Reversi\reversi.py";
                var eng = IronPython.Hosting.Python.CreateEngine();
                var scope = eng.CreateScope();
                eng.Execute(File.ReadAllText(path),scope);
                return scope.GetVariable("play")(w0.Flatten(),c0.val,w1.Flatten(),c1.val);
            });
        }


    }
}
