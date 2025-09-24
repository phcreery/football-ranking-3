Football Ranking

# FastAPI Project Template

A template repository for a FastAPI project that can automatically generate Unit files for easy project management using Systemd to start, restart, and stop the project.

# How to Use?

## 3. Sync the environment

```bash
# Set up the environment
# In a production environment, you can add --no-dev to all sync commands
# to reduce the installation of unnecessary dependencies
uv sync
```

## 4. Develop the project

```bash
# During development, try hot-reloading the project, which by default monitors all *.py files and .envs files
uv run dev
# Start the project
uv run start
```

First, define the necessary environment variables in the `AppConfig` and `UnicornConfig` in `config.py`, and provide default values. If you need to change the default values or if no default values are set, you need to define them in the `.env`.

Original matlab code

```matlab
clc
clear
close all
% s is score matrix
SO = readmatrix('College_football_2021.xlsx','Range',[2 2 131 131]);
SO(isnan(SO)) = 0;
names = readcell('College_football_2021.xlsx','Range','A2:A131');
% offensive based rankings
r1 = abs(null(SO-diag(sum(SO,1))));
% defensive based rankings
SD = (SO');
SD(isinf(SD)) = 0;
r2 = abs(null(SD-diag(sum(SD,1))));
% combined
r = r1./r2;
[B,i] = sort(r,'descend');
% i
out = fopen('rankings.txt','w');
for n = 1:length(i)
    fprintf(out,'%d. %s\n', n, names{i(n)});
end
fclose(out);
```
